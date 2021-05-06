import io
import sys
import xml.etree.ElementTree
import random
import re
import os
import yaml

from dvcrecord import PipelineStage
from dvcrecord.deps import make_parser

stage = PipelineStage('prepare')

split = stage.params.load('prepare.split')
random.seed(stage.params.load('prepare.seed'))

#get the whole trackedfile vs filename thing sorted out
input_file = stage.deps.from_cli()[0]
output_folder = stage.outputs.register('data', 'prepared')
output_test = os.path.join(output_folder, 'test.tsv')
output_train = os.path.join(output_folder, 'train.tsv')

def process_posts(fd_in, fd_out_train, fd_out_test, target_tag):
    num = 1
    for line in fd_in:
        try:
            fd_out = fd_out_train if random.random() > split else fd_out_test
            attr = xml.etree.ElementTree.fromstring(line).attrib

            pid = attr.get('Id', '')
            label = 1 if target_tag in attr.get('Tags', '') else 0
            title = re.sub(r'\s+', ' ', attr.get('Title', '')).strip()
            body = re.sub(r'\s+', ' ', attr.get('Body', '')).strip()
            text = title + ' ' + body

            fd_out.write(u'{}\t{}\t{}\n'.format(pid, label, text))

            num += 1
        except Exception as ex:
            sys.stderr.write(f'Skipping the broken line {num}: {ex}\n')


os.makedirs(os.path.join('data', 'prepared'), exist_ok=True)

with io.open(input_file, encoding='utf8') as fd_in:
    with io.open(output_train, 'w', encoding='utf8') as fd_out_train:
        with io.open(output_test, 'w', encoding='utf8') as fd_out_test:
            process_posts(fd_in, fd_out_train, fd_out_test, '<python>')

