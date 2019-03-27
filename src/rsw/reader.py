from ..io.reader import BinaryFileReader
from .rsw import Rsw


class RswReader(object):
    def __init__(self):
        pass

    @staticmethod
    def from_file(path):
        rsw = Rsw()
        with open(path, 'rb') as f:
            print(path)
            reader = BinaryFileReader(f)
            magic = reader.read('4s')[0]
            if magic != b'GRSW':
                raise RuntimeError('Invalid file type.')
            not_sure = reader.read('H')  # 258
            rsw.ini_file = reader.read_fixed_length_null_terminated_string(40)
            rsw.gnd_file = reader.read_fixed_length_null_terminated_string(40)
            rsw.gat_file = reader.read_fixed_length_null_terminated_string(40)
            rsw.src_file = reader.read_fixed_length_null_terminated_string(40)
            # WATER
            rsw.water.height = reader.read('f')[0]
            rsw.water.type = reader.read('I')[0]
            rsw.water.amplitude = reader.read('f')[0]
            rsw.water.phase = reader.read('f')[0]
            rsw.water.surface_curve_level = reader.read('f')[0]
            rsw.water.texture_cycling = reader.read('I')[0]

            print(reader.tell())

            # LIGHT
            garbo = reader.read('2I')  # garbo? (45, 15)

            rsw.light.ambient = reader.read('3f')
            rsw.light.diffuse = reader.read('3f')
            rsw.light.alpha = reader.read('f')[0]

            print(rsw.light.ambient)
            print(rsw.light.diffuse)
            print(rsw.light.alpha)

            # unknown = reader.read('I')[0]
            object_counts = reader.read('5I')
            print(object_counts)
            object_count = object_counts[4]
            print('obj')
            print(object_count)
            for i in range(object_count):
                object_type = reader.read('I')[0]
                # print(object_type)
                if object_type == 1:
                    model = Rsw.Model()
                    model.name = reader.read_fixed_length_null_terminated_string(40)
                    unk1 = reader.read('3f')
                    model.filename = reader.read_fixed_length_null_terminated_string(40)
                    # print(model.name, model.filename)
                    model.reserved = reader.read('40B')
                    model.type = reader.read_fixed_length_null_terminated_string(20)
                    unk2 = reader.read('15I')
                    model.position = reader.read('3f')
                    model.rotation = reader.read('3f')
                    model.scale = reader.read('3f')
                    rsw.models.append(model)
                elif object_type == 2:
                    light = Rsw.LightSource()
                    reader.read('108B')
                    rsw.light_sources.append(light)
                elif object_type == 3:
                    sound = Rsw.Sound()
                    reader.read('192B')
                    rsw.sounds.append(sound)
                elif object_type == 4:
                    effect = Rsw.Effect()
                    reader.read('116B')
                    rsw.effects.append(effect)
                else:
                    raise RuntimeError('Invalid object type.')

        return rsw
