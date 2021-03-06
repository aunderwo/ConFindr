import os
import subprocess
import pytest

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0, parentdir)
from confindr.confindr import *
from Bio import SeqIO

# TODO: Make these far more useful than they currently are.


def test_present_dependency():
    assert dependency_check('ls') is True


def test_nonexistent_dependency():
    assert dependency_check('fake_dependency') is False


def test_r1_fastqs():
    assert find_paired_reads('tests/fake_fastqs/') == [['tests/fake_fastqs/test_R1.fastq.gz',
                                                        'tests/fake_fastqs/test_R2.fastq.gz']]


def test_1_fastqs():
    assert find_paired_reads('tests/fake_fastqs/', forward_id='_1',
                             reverse_id='_2') == [['tests/fake_fastqs/test_1.fastq.gz',
                                                   'tests/fake_fastqs/test_2.fastq.gz']]


def test_empty_fastqs():
    assert find_paired_reads('tests/fake_fastqs/', forward_id='_asdf', reverse_id='_fdsa') == []


def test_unpaired_fastq():
    assert ['tests/fake_fastqs/test_alone.fastq.gz'] == find_unpaired_reads('tests/fake_fastqs')[2]


def test_correct_num_multipositions():
    contig_names = list()
    for contig in SeqIO.parse('tests/rmlst.fasta', 'fasta'):
        contig_names.append(contig.id)
    multi_positions = 0
    for contig_name in contig_names:
        multi_position_dict = read_contig(contig_name=contig_name,
                                          bamfile_name='tests/contamination.bam',
                                          reference_fasta='tests/rmlst.fasta',
                                          report_file='tests/dummy_report',
                                          quality_cutoff=20,
                                          base_cutoff=2)
        multi_positions += len(multi_position_dict)
    os.remove('tests/dummy_report')
    assert multi_positions == 15


def test_correct_percent_contam():
    percent_contam, stddev = estimate_percent_contamination('tests/example_contamination.csv')
    assert percent_contam == '18.20'
    assert stddev == '5.89'


def test_run_cmd_success():
    cmd = 'echo asdf'
    out, err = run_cmd(cmd)
    assert out == 'asdf\n'
    assert err == ''


def test_run_cmd_failure_exit_code():
    with pytest.raises(subprocess.CalledProcessError):
        run_cmd('garbagecommandthatdoesnotwork')


def test_two_quality_bases_present():
    assert has_two_high_quality_bases([20, 20]) is True


def test_two_quality_bases_not_present():
    assert has_two_high_quality_bases([10, 22, 3]) is False


def test_quality_bases_success_custom_params():
    assert has_two_high_quality_bases([30, 22, 44], quality_cutoff=22, base_count_cutoff=3) is True


def test_quality_bases_fail_custom_params():
    assert has_two_high_quality_bases([30, 22, 44], quality_cutoff=30, base_count_cutoff=3) is False
