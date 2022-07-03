from stog.data.dataset_readers.sig_parsing.io import SIGIO


class NodeRestore:

    def __init__(self, node_utils):
        self.node_utils = node_utils

    def restore_instance(self, sig):
        graph = sig.graph
        for node in graph.get_nodes():
            instance = node.instance
            new_instance = self.node_utils.get_frames(instance)[0]
            if instance != new_instance:
                graph.replace_node_attribute(node, 'instance', instance, new_instance)
            continue

    def restore_file(self, file_path):
        for sig in SIGIO.read(file_path):
            self.restore_instance(sig)
            yield sig


if __name__ == '__main__':
    import argparse

    from stog.data.dataset_readers.sig_parsing.node_utils import NodeUtilities as NU

    parser = argparse.ArgumentParser('node_restore.py')
    parser.add_argument('--sig_files', nargs='+', required=True)
    parser.add_argument('--util_dir', default='./temp')

    args = parser.parse_args()

    node_utils = NU.from_json(args.util_dir, 0)

    nr = NodeRestore(node_utils)

    for file_path in args.sig_files:
        with open(file_path + '.frame', 'w', encoding='utf-8') as f:
            for sig in nr.restore_file(file_path):
                f.write(str(sig) + '\n\n')
