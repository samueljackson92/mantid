import math
from abc import (ABCMeta, abstractmethod)
from SANS2.Common.SANSType import (SANSInstrument, SampleShape, convert_int_to_shape, DataType)
from SANS2.Common.SANSFunctions import create_unmanaged_algorithm
from SANS2.Common.SANSConstants import SANSConstants


class DivideByVolume(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        super(DivideByVolume, self).__init__()

    @abstractmethod
    def divide_by_volume(self, workspace, scale_info):
        pass


class NullDivideByVolume(DivideByVolume):
    def __init__(self):
        super(NullDivideByVolume, self).__init__()

    def divide_by_volume(self, workspace, scale_info):
        _ = scale_info
        return workspace


class DivideByVolumeISIS(DivideByVolume):

    def __init__(self):
        super(DivideByVolumeISIS, self).__init__()

    def divide_by_volume(self, workspace, scale_info):
        volume = self._get_volume(workspace, scale_info)
        inverse_volume = 1./volume
        divide_name = "Scale"
        divide_options = {SANSConstants.input_workspace: workspace,
                          SANSConstants.output_workspace: SANSConstants.dummy,
                          "Factor": inverse_volume,
                          "Operation": "Multiply"}
        divide_alg = create_unmanaged_algorithm(divide_name, **divide_options)
        divide_alg.execute()
        return divide_alg.getProperty(SANSConstants.output_workspace).value

    def _get_volume(self, workspace, scale_info):
        # Get the geometry information from the workspace
        sample_details = workspace.sample()

        # If the sample details are specified in the state, then use
        # this information else use the information stored on the workspace
        try:
            shape = scale_info.shape if scale_info.shape is not None else \
                convert_int_to_shape(sample_details.getGeometryFlag())
        except ValueError:
            shape = SampleShape.CylinderAxisAlong

        thickness = scale_info.thickness if scale_info.thickness is not None else sample_details.getThickness()
        width = scale_info.width if scale_info.width is not None else sample_details.getWidth()
        height = scale_info.height if scale_info.height is not None else sample_details.getHeight()

        # Now we calculate the volume
        if shape is SampleShape.CylinderAxisUp:
            # Volume = circle area * height
            # Factor of four comes from radius = width/2
            volume = height * math.pi
            volume *= math.pow(width, 2) / 4.0
        elif shape is SampleShape.Cuboid:
            # Flat plate sample
            volume = width * height * thickness
        elif shape is SampleShape.CylinderAxisAlong:
            # Factor of four comes from radius = width/2
            # Disc - where height is not used
            volume = thickness * math.pi
            volume *= math.pow(width, 2) / 4.0
        else:
            raise NotImplementedError('DivideByVolumeISIS: The shape {0} is not in the list of supported shapes'.format(shape))
        return volume


class DivideByVolumeFactory(object):
    def __init__(self):
        super(DivideByVolumeFactory, self).__init__()

    @staticmethod
    def create_divide_by_volume(state, data_type):
        data = state.data
        instrument = data.instrument

        is_isis_instrument = instrument is SANSInstrument.LARMOR or instrument is SANSInstrument.SANS2D or\
                             instrument is SANSInstrument.LOQ
        if is_isis_instrument and data_type is DataType.Sample:
            divider = DivideByVolumeISIS()
        elif is_isis_instrument:
            divider = NullDivideByVolume()
        else:
            raise RuntimeError("DivideVolumeFactory: Other instruments are not implemented yet.")
        return divider


class MultiplyByAbsoluteScale(object):
    __metaclass__ = ABCMeta
    DEFAULT_SCALING = 100.0

    def __init__(self):
        super(MultiplyByAbsoluteScale, self).__init__()

    @staticmethod
    def do_scale(workspace, scale_factor):
        scale_name = "Scale"
        scale_options = {SANSConstants.input_workspace: workspace,
                         SANSConstants.output_workspace: SANSConstants.dummy,
                         "Factor": scale_factor,
                         "Operation": "Multiply"}
        scale_alg = create_unmanaged_algorithm(scale_name, **scale_options)
        scale_alg.execute()
        return scale_alg.getProperty(SANSConstants.output_workspace).value

    @abstractmethod
    def multiply_by_absolute_scale(self, workspace, scale_info):
        pass


class MultiplyByAbsoluteScaleLOQ(MultiplyByAbsoluteScale):
    def __init__(self):
        super(MultiplyByAbsoluteScaleLOQ, self).__init__()

    def multiply_by_absolute_scale(self, workspace, scale_info):
        scale_factor = scale_info.scale*self.DEFAULT_SCALING if scale_info.scale is not None else self.DEFAULT_SCALING
        rescale_to_colette = math.pi
        scale_factor /= rescale_to_colette
        return self.do_scale(workspace, scale_factor)


class MultiplyByAbsoluteScaleISIS(MultiplyByAbsoluteScale):
    def __init__(self):
        super(MultiplyByAbsoluteScaleISIS, self).__init__()

    def multiply_by_absolute_scale(self, workspace, scale_info):
        scale_factor = scale_info.scale*self.DEFAULT_SCALING if scale_info.scale is not None else self.DEFAULT_SCALING
        return self.do_scale(workspace, scale_factor)


class MultiplyByAbsoluteScaleFactory(object):
    def __init__(self):
        super(MultiplyByAbsoluteScaleFactory, self).__init__()

    @staticmethod
    def create_multiply_by_absolute(state):
        data = state.data
        instrument = data.instrument

        is_isis_instrument = instrument is SANSInstrument.LARMOR or instrument is SANSInstrument.SANS2D or SANSInstrument.LOQ
        if instrument is SANSInstrument.LOQ:
            multiplier = MultiplyByAbsoluteScaleLOQ()
        elif is_isis_instrument:
            multiplier = MultiplyByAbsoluteScaleISIS()
        else:
            raise NotImplementedError("MultiplyByAbsoluteScaleFactory: Other instruments are not implemented yet.")
        return multiplier
