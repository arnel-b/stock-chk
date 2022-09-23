import json
import os
import shutil

class JW():

    def __init__(self):
        pass

    def append_json(self, data, folder, fname, create_copy=False):

        if os.path.isfile("{}/{}".format(folder, fname)):
            # print("existing", "{}/{}".format(dir, fname))
            pkl_file = open('{}/{}'.format(folder, fname))
            full_dict = json.load(pkl_file)
            full_dict.append(data)
            pkl_file.close()
            p_writer = open('{}/{}'.format(folder, fname), 'w', encoding='utf-8')
            json.dump(full_dict, p_writer, indent=4)
            p_writer.close()

            if create_copy:
                shutil.copy(os.path.join(folder,fname), os.path.join('json_copy', fname))

        else:
            full_dict = [data]
            p_writer = open('{}/{}'.format(folder, fname), 'w', encoding='utf-8')
            json.dump(full_dict, p_writer, indent=4)
            p_writer.close()
            # print('creating','{}/{}'.format(dir, fname))