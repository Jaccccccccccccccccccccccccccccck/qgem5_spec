import os
import sys
import argparse
import pexpect
import time
import logging
import json

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT)

parser = argparse.ArgumentParser(description='--channel=channel')
parser.add_argument("--channel", type=int, default=1)
parser.add_argument("--mode", type=str)
parser.add_argument("--benchmark", type=str)
parser.add_argument("--benchmark_type", type=str)
parser.add_argument("--benchmark_index", type=int)
args = parser.parse_args()

CHANNEL = str(args.channel)

os.environ['LD_LIBRARY_PATH'] = os.environ['HOME'] + '/qr'

benchmark_base_dir = '/home'
OUT_PATH = '/home/test/'
QEMU_PATH = '/home/workspace/interqrio/qemu-4.1.1/aarch64-softmmu/'
QEMU_GEM5_PATH = '/home/workspace/qemu-gem5/gem5-21.1.0.2/'
GEM5_PATH = '/home/workspace/gem5/'
KERNEL_PATH = '/home/Image4.4'
HDA_PATH = '/home/ppi_benchmark_210928.img'

# 1000 * 24 * 60m * 60s/m
TIMEOUT = 86400000

QEMU_COMMAND = QEMU_PATH + 'qemu-system-aarch64 \
    -qrtag -machine virt,virtualization=true,gic-version=3 -nographic \
    -m size=1024M \
    -cpu cortex-a57 \
    -smp cpus=1 \
    -kernel ' + KERNEL_PATH + ' \
    -hda ' + HDA_PATH + ' \
    -append "root=/dev/vda rw console=ttyAMA0 rdinit=/linuxrc" \
    -channel ' + CHANNEL + ' \
    -clockRate 1'

QGEM5_COMMAND = QEMU_GEM5_PATH + 'build/ARM/gem5.opt \
    --outdir={}  \
    ' + QEMU_GEM5_PATH + '/configs/example/se.py \
    -n 1 \
    --cmd={} \
    --options="{}" \
    --cpu-type=TimingSimpleCPU \
    --caches \
    --mem-size=1099511627775'

GEM5_COMMAND = 'nohup bash -c \'time ' + GEM5_PATH + 'build/ARM/gem5.opt ' \
    '--outdir={} ' \
    + GEM5_PATH + 'configs/example/se.py ' \
    '--cpu-type=TimingSimpleCPU ' \
    '--mem-size=8GB ' \
    '--caches ' \
    '-n 1 ' \
    '--cmd={} ' \
    '--options="{}" > ' + OUT_PATH + 'gem5-script-{}.out & \''

ALL_TEST_BENCHMARKS = [
    {'name': '400.perlbench',
     'index': 1,
     'type': 'int',
     'dir': '/benchmark/400.perlbench/run/run_base_test_qemurio.0000',
     'cmd': '/benchmark/400.perlbench/exe/perlbench_base.qemurio -I. -I./lib attrs.pl',
     },
    {'name': '400.perlbench',
     'index': 2,
     'type': 'int',
     'dir': '/benchmark/400.perlbench/run/run_base_test_qemurio.0000',
     'cmd': '/benchmark/400.perlbench/exe/perlbench_base.qemurio  -I. -I./lib gv.pl',
     },
    {'name': '400.perlbench',
     'index': 3,
     'type': 'int',
     'dir': '/benchmark/400.perlbench/run/run_base_test_qemurio.0000',
     'cmd': '/benchmark/400.perlbench/exe/perlbench_base.qemurio -I. -I./lib makerand.pl',
     },
    {'name': '400.perlbench',
     'index': 4,
     'type': 'int',
     'dir': '/benchmark/400.perlbench/run/run_base_test_qemurio.0000',
     'cmd': '/benchmark/400.perlbench/exe/perlbench_base.qemurio -I. -I./lib pack.pl',
     },
    {'name': '400.perlbench',
     'index': 5,
     'type': 'int',
     'dir': '/benchmark/400.perlbench/run/run_base_test_qemurio.0000',
     'cmd': '/benchmark/400.perlbench/exe/perlbench_base.qemurio -I. -I./lib redef.pl',
     },
    {'name': '400.perlbench',
     'index': 6,
     'type': 'int',
     'dir': '/benchmark/400.perlbench/run/run_base_test_qemurio.0000',
     'cmd': '/benchmark/400.perlbench/exe/perlbench_base.qemurio -I. -I./lib ref.pl',
     },
    {'name': '400.perlbench',
     'index': 7,
     'type': 'int',
     'dir': '/benchmark/400.perlbench/run/run_base_test_qemurio.0000',
     'cmd': '/benchmark/400.perlbench/exe/perlbench_base.qemurio -I. -I./lib regmesg.pl',
     },

    {'name': '400.perlbench',
     'index': 8,
     'type': 'int',
     'dir': '/benchmark/400.perlbench/run/run_base_test_qemurio.0000',
     'cmd': '/benchmark/400.perlbench/exe/perlbench_base.qemurio -I. -I./lib test.pl',
     },
    {'name': '401.bzip2',
     'index': 1,
     'type': 'int',
     'dir': '/benchmark/401.bzip2/run/run_base_test_qemurio.0000',
     'cmd': '/benchmark/401.bzip2/exe/bzip2_base.qemurio input.program 5',
     },
    {'name': '401.bzip2',
     'index': 2,
     'type': 'int',
     'dir': '/benchmark/401.bzip2/run/run_base_test_qemurio.0000',
     'cmd': '/benchmark/401.bzip2/exe/bzip2_base.qemurio dryer.jpg 2',
     },
    {'name': '403.gcc',
     'index': 1,
     'type': 'int',
     'dir': '/benchmark/403.gcc/run/run_base_test_qemurio.0000',
     'cmd': '/benchmark/403.gcc/exe/gcc_base.qemurio cccp.i -o cccp.s',
     },
    {'name': '429.mcf',
     'index': 1,
     'type': 'int',
     'dir': '/benchmark/429.mcf/run/run_base_test_qemurio.0000',
     'cmd': '/benchmark/429.mcf/exe/mcf_base.qemurio inp.in',
     },
    {'name': '445.gobmk',
     'index': 1,
     'type': 'int',
     'dir': '/benchmark/445.gobmk/run/run_base_test_qemurio.0000',
     'cmd': '/benchmark/445.gobmk/exe/gobmk_base.qemurio --quiet --mode gtp <capture.tst',

     },
    {'name': '445.gobmk',
     'index': 2,
     'type': 'int',
     'dir': '/benchmark/445.gobmk/run/run_base_test_qemurio.0000',
     'cmd': '/benchmark/445.gobmk/exe/gobmk_base.qemurio --quiet --mode gtp <connect.tst',
     },
    {'name': '445.gobmk',
     'index': 3,
     'type': 'int',
     'dir': '/benchmark/445.gobmk/run/run_base_test_qemurio.0000',
     'cmd': '/benchmark/445.gobmk/exe/gobmk_base.qemurio --quiet --mode gtp <connect_rot.tst',
     },
    {'name': '445.gobmk',
     'index': 4,
     'type': 'int',
     'dir': '/benchmark/445.gobmk/run/run_base_test_qemurio.0000',
     'cmd': '/benchmark/445.gobmk/exe/gobmk_base.qemurio --quiet --mode gtp <connection.tst',
     },
    {'name': '445.gobmk',
     'index': 5,
     'type': 'int',
     'dir': '/benchmark/445.gobmk/run/run_base_test_qemurio.0000',
     'cmd': '/benchmark/445.gobmk/exe/gobmk_base.qemurio --quiet --mode gtp <connection_rot.tst',
     },
    {'name': '445.gobmk',
     'index': 6,
     'type': 'int',
     'dir': '/benchmark/445.gobmk/run/run_base_test_qemurio.0000',
     'cmd': '/benchmark/445.gobmk/exe/gobmk_base.qemurio --quiet --mode gtp <cutstone.tst',
     },
    {'name': '445.gobmk',
     'index': 7,
     'type': 'int',
     'dir': '/benchmark/445.gobmk/run/run_base_test_qemurio.0000',
     'cmd': '/benchmark/445.gobmk/exe/gobmk_base.qemurio --quiet --mode gtp <dniwog.tst',
     },
    {'name': '456.hmmer',
     'index': 1,
     'type': 'int',
     'dir': '/benchmark/456.hmmer/run/run_base_test_qemurio.0000',
     'cmd': '/benchmark/456.hmmer/exe/hmmer_base.qemurio --fixed 0 --mean 325 --num 45000 --sd 200 --seed 0 bombesin.hmm',
     },
    {'name': '458.sjeng',
     'index': 1,
     'type': 'int',
     'dir': '/benchmark/458.sjeng/run/run_base_test_qemurio.0000',
     'cmd': '/benchmark/458.sjeng/exe/sjeng_base.qemurio test.txt',
     },
    {'name': '462.libquantum',
     'index': 1,
     'type': 'int',
     'dir': '/benchmark/462.libquantum/run/run_base_test_qemurio.0000',
     'cmd': '/benchmark/462.libquantum/exe/libquantum_base.qemurio 33 5',
     },
    {'name': '464.h264ref',
     'index': 1,
     'type': 'int',
     'dir': '/benchmark/464.h264ref/run/run_base_test_qemurio.0000',
     'cmd': '/benchmark/464.h264ref/exe/h264ref_base.qemurio -d foreman_test_encoder_baseline.cfg',
     },
    {'name': '471.omnetpp',
     'index': 1,
     'type': 'int',
     'dir': '/benchmark/471.omnetpp/run/run_base_test_qemurio.0000',
     'cmd': '/benchmark/471.omnetpp/exe/omnetpp_base.qemurio omnetpp.ini',
     },
    {'name': '473.astar',
     'index': 1,
     'type': 'int',
     'dir': '/benchmark/473.astar/run/run_base_test_qemurio.0000',
     'cmd': '/benchmark/473.astar/exe/astar_base.qemurio lake.cfg',
     },
    {'name': '483.xalancbmk',
     'index': 1,
     'type': 'int',
     'dir': '/benchmark/483.xalancbmk/run/run_base_test_qemurio.0000',
     'cmd': '/benchmark/483.xalancbmk/exe/Xalan_base.qemurio -v test.xml xalanc.xsl',
     },
    # fp
    {'name': '410.bwaves',
     'index': 1,
     'type': 'fp',
     'dir': '/benchmark/410.bwaves/data/test/input',
     'cmd': '/benchmark/410.bwaves/exe/bwaves_base.qemurio',
     },
    {'name': '416.gamess',
     'index': 1,
     'type': 'fp',
     'dir': '/benchmark/416.gamess/data/test/input',
     'cmd': '/benchmark/416.gamess/exe/gamess_base.qemurio <exam29.config',
     },
    {'name': '433.milc',
     'index': 1,
     'type': 'fp',
     'dir': '/benchmark/433.milc/data/test/input',
     'cmd': '/benchmark/433.milc/exe/milc_base.qemurio <su3imp.in',
     },
    {'name': '435.gromacs',
     'index': 1,
     'type': 'fp',
     'dir': '/benchmark/435.gromacs/data/test/input',
     'cmd': '/benchmark/435.gromacs/exe/gromacs_base.qemurio -silent -deffnm gromacs -nice 0',
     },
    {'name': '436.cactusADM',
     'index': 1,
     'type': 'fp',
     'dir': '/benchmark/436.cactusADM/data/test/input',
     'cmd': '/benchmark/436.cactusADM/exe/cactusADM_base.qemurio benchADM.par',
     },
    {'name': '437.leslie3d',
     'index': 1,
     'type': 'fp',
     'dir': '/benchmark/437.leslie3d/data/test/input',
     'cmd': '/benchmark/437.leslie3d/exe/leslie3d_base.qemurio <leslie3d.in',
     },
    {'name': '444.namd',
     'index': 1,
     'type': 'fp',
     'dir': '/benchmark/444.namd/data/all/input',
     'cmd': '/benchmark/444.namd/exe/namd_base.qemurio --input namd.input --iterations 1 --output namd.out',
     },
    {'name': '447.dealII',
     'index': 1,
     'type': 'fp',
     'dir': '/benchmark/447.dealII/data/all/input',
     'cmd': '/benchmark/447.dealII/exe/dealII_base.qemurio 8',
     },
    {'name': '450.soplex',
     'index': 1,
     'type': 'fp',
     'dir': '/benchmark/450.soplex/data/test/input',
     'cmd': '/benchmark/450.soplex/exe/soplex_base.qemurio -m10000 test.mps',
     },
    {'name': '453.povray',
     'index': 1,
     'type': 'fp',
     'dir': '/benchmark/453.povray/data/test/input',
     'cmd': '/benchmark/453.povray/exe/povray_base.qemurio SPEC-benchmark-test.ini',
     },
    {'name': '454.calculix',
     'index': 1,
     'type': 'fp',
     'dir': '/benchmark/454.calculix/data/test/input',
     'cmd': '/benchmark/454.calculix/exe/calculix_base.qemurio -i beampic',
     },
    {'name': '459.GemsFDTD',
     'index': 1,
     'type': 'fp',
     'dir': '/benchmark/459.GemsFDTD/data/test/input',
     'cmd': '/benchmark/459.GemsFDTD/exe/GemsFDTD_base.qemurio',
     },
    {'name': '465.tonto',
     'index': 1,
     'type': 'fp',
     'dir': '/benchmark/465.tonto/data/test/input',
     'cmd': '/benchmark/465.tonto/exe/tonto_base.qemurio',
     },
    {'name': '470.lbm',
     'index': 1,
     'type': 'fp',
     'dir': '/benchmark/470.lbm/data/test/input',
     'cmd': '/benchmark/470.lbm/exe/lbm_base.qemurio 20 reference.dat 0 1 100_100_130_cf_a.of',
     },
    {'name': '482.sphinx3',
     'index': 1,
     'type': 'fp',
     'dir': '/benchmark/482.sphinx3/run/run_base_test_qemurio.0000',
     'cmd': '/benchmark/482.sphinx3/exe/sphinx_livepretend_base.qemurio ctlfile . args.an4',
     }
]
ALL_REF_BENCHMARKS = [
    {'name': '410.bwaves',
     'index': 1,
     'type': 'fp',
     'dir': '/benchmark/410.bwaves/data/ref/input',
     'cmd': '/benchmark/410.bwaves/exe/bwaves_base.qemurio',
     },
    {'name': '416.gamess_cystosine',
     'index': 1,
     'type': 'fp',
     'dir': '/benchmark/416.gamess/data/ref/input',
     'cmd': '/benchmark/416.gamess/exe/gamess_base.qemurio <cytosine.2.config',
     },
    {'name': '416.gamess_h2ocu2+.gradient',
     'index': 2,
     'type': 'fp',
     'dir': '/benchmark/416.gamess/data/ref/input',
     'cmd': '/benchmark/416.gamess/exe/gamess_base.qemurio <h2ocu2+.gradient.config',
     },
    {'name': '416.gamess_triazolium',
     'index': 3,
     'type': 'fp',
     'dir': '/benchmark/416.gamess/data/ref/input',
     'cmd': '/benchmark/416.gamess/exe/gamess_base.qemurio <triazolium.config',
     },
    {'name': '433.milc',
     'index': 1,
     'type': 'fp',
     'dir': '/benchmark/433.milc/data/ref/input',
     'cmd': '/benchmark/433.milc/exe/milc_base.qemurio <su3imp.in',
     },
    {'name': '435.gromacs',
     'index': 1,
     'type': 'fp',
     'dir': '/benchmark/435.gromacs/data/ref/input',
     'cmd': '/benchmark/435.gromacs/exe/gromacs_base.qemurio -silent -deffnm gromacs -nice 0',
     },
    {'name': '436.cactusADM',
     'index': 1,
     'type': 'fp',
     'dir': '/benchmark/436.cactusADM/data/ref/input',
     'cmd': '/benchmark/436.cactusADM/exe/cactusADM_base.qemurio benchADM.par',
     },
    {'name': '437.leslie3d',
     'index': 1,
     'type': 'fp',
     'dir': '/benchmark/437.leslie3d/data/ref/input',
     'cmd': '/benchmark/437.leslie3d/exe/leslie3d_base.qemurio <leslie3d.in',
     },
    {'name': '444.namd',
     'index': 1,
     'type': 'fp',
     'dir': '/benchmark/444.namd/data/all/input',
     'cmd': '/benchmark/444.namd/exe/namd_base.qemurio --input namd.input --iterations 38 --output namd.out',
     },
    {'name': '447.dealII',
     'index': 1,
     'type': 'fp',
     'dir': '/benchmark/447.dealII/data/all/input',
     'cmd': '/benchmark/447.dealII/exe/dealII_base.qemurio 23',
     },
    {'name': '450.soplex',
     'index': 1,
     'type': 'fp',
     'dir': '/benchmark/450.soplex/data/ref/input',
     'cmd': '/benchmark/450.soplex/exe/soplex_base.qemurio -s1 -e -m45000 pds-50.mps',
     },
    {'name': '450.soplex',
     'index': 2,
     'type': 'fp',
     'dir': '/benchmark/450.soplex/data/ref/input',
     'cmd': '/benchmark/450.soplex/exe/soplex_base.qemurio -m3500 ref.mps',
     },
    {'name': '453.povray',
     'index': 1,
     'type': 'fp',
     'dir': '/benchmark/453.povray/run/run_base_ref_qemurio.0000',
     'cmd': '/benchmark/453.povray/exe/povray_base.qemurio SPEC-benchmark-ref.ini',
     },
    {'name': '454.calculix',
     'index': 1,
     'type': 'fp',
     'dir': '/benchmark/454.calculix/data/ref/input',
     'cmd': '/benchmark/454.calculix/exe/calculix_base.qemurio -i hyperviscoplastic',
     },
    {'name': '459.GemsFDTD',
     'index': 1,
     'type': 'fp',
     'dir': '/benchmark/459.GemsFDTD/data/ref/input',
     'cmd': '/benchmark/459.GemsFDTD/exe/GemsFDTD_base.qemurio',
     },
    {'name': '465.tonto',
     'index': 1,
     'type': 'fp',
     'dir': '/benchmark/465.tonto/data/ref/input',
     'cmd': '/benchmark/465.tonto/exe/tonto_base.qemurio',
     },
    {'name': '470.lbm',
     'index': 1,
     'type': 'fp',
     'dir': '/benchmark/470.lbm/data/ref/input',
     'cmd': '/benchmark/470.lbm/exe/lbm_base.qemurio 3000 reference.dat 0 0 100_100_130_ldc.of',
     },
    # {'name': '481.wrf',
    #  'type': 'fp',
    #  'dir': '/benchmark/481.wrf/data/ref/input',
    #  'cmd': '/benchmark/481.wrf/exe/wrf_base.qemurio',
    #  },
    # {'name': '482.sphinx3',
    #  'type': 'fp',
    #  'dir': '/benchmark/482.sphinx3/run/run_base_ref_qemurio.0000/',
    #  'cmd': '/benchmark/482.sphinx3/exe/sphinx_livepretend_base.qemurio ctlfile . args.an4',
    #  },
    {'name': '400.perlbench',
     'index': 1,
     'type': 'int',
     'dir': '/benchmark/400.perlbench/run/run_base_ref_qemurio.0000',
     'cmd': '/benchmark/400.perlbench/exe/perlbench_base.qemurio -I./lib checkspam.pl 2500 5 25 11 150 1 1 1 1',
     },
    {'name': '400.perlbench',
     'index': 2,
     'type': 'int',
     'dir': '/benchmark/400.perlbench/run/run_base_ref_qemurio.0000',
     'cmd': '/benchmark/400.perlbench/exe/perlbench_base.qemurio -I./lib diffmail.pl 4 800 10 17 19 300',
     },
    {'name': '400.perlbench',
     'index': 3,
     'type': 'int',
     'dir': '/benchmark/400.perlbench/run/run_base_ref_qemurio.0000',
     'cmd': '/benchmark/400.perlbench/exe/perlbench_base.qemurio -I./lib splitmail.pl 1600 12 26 16 4500',
     },
    {'name': '401.bzip2',
     'index': 1,
     'type': 'int',
     'dir': '/benchmark/401.bzip2/run/run_base_ref_qemurio.0000',
     'cmd': '/benchmark/401.bzip2/exe/bzip2_base.qemurio input.source 280',
     },
    {'name': '401.bzip2',
     'index': 2,
     'type': 'int',
     'dir': '/benchmark/401.bzip2/run/run_base_ref_qemurio.0000',
     'cmd': '/benchmark/401.bzip2/exe/bzip2_base.qemurio chicken.jpg 30',
     },
    {'name': '401.bzip2',
     'index': 3,
     'type': 'int',
     'dir': '/benchmark/401.bzip2/run/run_base_ref_qemurio.0000',
     'cmd': '/benchmark/401.bzip2/exe/bzip2_base.qemurio liberty.jpg 30',
     },
    {'name': '401.bzip2',
     'index': 4,
     'type': 'int',
     'dir': '/benchmark/401.bzip2/run/run_base_ref_qemurio.0000',
     'cmd': '/benchmark/401.bzip2/exe/bzip2_base.qemurio input.program 280',
     },
    {'name': '401.bzip2',
     'index': 5,
     'type': 'int',
     'dir': '/benchmark/401.bzip2/run/run_base_ref_qemurio.0000',
     'cmd': '/benchmark/401.bzip2/exe/bzip2_base.qemurio text.html 280',
     },
    {'name': '401.bzip2',
     'index': 6,
     'type': 'int',
     'dir': '/benchmark/401.bzip2/run/run_base_ref_qemurio.0000',
     'cmd': '/benchmark/401.bzip2/exe/bzip2_base.qemurio input.combined 200',
     },
    {'name': '403.gcc',
     'index': 1,
     'type': 'int',
     'dir': '/benchmark/403.gcc/run/run_base_ref_qemurio.0000',
     'cmd': '/benchmark/403.gcc/exe/gcc_base.qemurio 166.i -o 166.s',
     },
    {'name': '403.gcc',
     'index': 2,
     'type': 'int',
     'dir': '/benchmark/403.gcc/run/run_base_ref_qemurio.0000',
     'cmd': '/benchmark/403.gcc/exe/gcc_base.qemurio 200.i -o 200.s',
     },
    {'name': '403.gcc',
     'index': 3,
     'type': 'int',
     'dir': '/benchmark/403.gcc/run/run_base_ref_qemurio.0000',
     'cmd': '/benchmark/403.gcc/exe/gcc_base.qemurio c-typeck.i -o c-typeck.s',
     },
    {'name': '403.gcc',
     'index': 4,
     'type': 'int',
     'dir': '/benchmark/403.gcc/run/run_base_ref_qemurio.0000',
     'cmd': '/benchmark/403.gcc/exe/gcc_base.qemurio cp-decl.i -o cp-decl.s',
     },
    {'name': '403.gcc',
     'index': 5,
     'type': 'int',
     'dir': '/benchmark/403.gcc/run/run_base_ref_qemurio.0000',
     'cmd': '/benchmark/403.gcc/exe/gcc_base.qemurio expr.i -o expr.s',
     },
    {'name': '403.gcc',
     'index': 6,
     'type': 'int',
     'dir': '/benchmark/403.gcc/run/run_base_ref_qemurio.0000',
     'cmd': '/benchmark/403.gcc/exe/gcc_base.qemurio expr2.i -o expr2.s',
     },
    {'name': '403.gcc',
     'index': 7,
     'type': 'int',
     'dir': '/benchmark/403.gcc/run/run_base_ref_qemurio.0000',
     'cmd': '/benchmark/403.gcc/exe/gcc_base.qemurio g23.i -o g23.s',
     },
    {'name': '403.gcc',
     'index': 8,
     'type': 'int',
     'dir': '/benchmark/403.gcc/run/run_base_ref_qemurio.0000',
     'cmd': '/benchmark/403.gcc/exe/gcc_base.qemurio s04.i -o s04.s',
     },
    {'name': '403.gcc',
     'index': 9,
     'type': 'int',
     'dir': '/benchmark/403.gcc/run/run_base_ref_qemurio.0000',
     'cmd': '/benchmark/403.gcc/exe/gcc_base.qemurio scilab.i -o scilab.s',
     },
    {'name': '429.mcf',
     'index': 1,
     'type': 'int',
     'dir': '/benchmark/429.mcf/run/run_base_ref_qemurio.0000',
     'cmd': '/benchmark/429.mcf/exe/mcf_base.qemurio inp.in',
     },
    {'name': '445.gobmk',
     'index': 1,
     'type': 'int',
     'dir': '/benchmark/445.gobmk/run/run_base_ref_qemurio.0000',
     'cmd': '/benchmark/445.gobmk/exe/gobmk_base.qemurio --quiet --mode gtp <13x13.tst',
     },
    {'name': '445.gobmk',
     'index': 2,
     'type': 'int',
     'dir': '/benchmark/445.gobmk/run/run_base_ref_qemurio.0000',
     'cmd': '/benchmark/445.gobmk/exe/gobmk_base.qemurio --quiet --mode gtp <nngs.tst',
     },
    {'name': '445.gobmk',
     'index': 3,
     'type': 'int',
     'dir': '/benchmark/445.gobmk/run/run_base_ref_qemurio.0000',
     'cmd': '/benchmark/445.gobmk/exe/gobmk_base.qemurio --quiet --mode gtp <score2.tst',
     },
    {'name': '445.gobmk',
     'index': 4,
     'type': 'int',
     'dir': '/benchmark/445.gobmk/run/run_base_ref_qemurio.0000',
     'cmd': '/benchmark/445.gobmk/exe/gobmk_base.qemurio --quiet --mode gtp <trevorc.tst',
     },
    {'name': '445.gobmk',
     'index': 5,
     'type': 'int',
     'dir': '/benchmark/445.gobmk/run/run_base_ref_qemurio.0000',
     'cmd': '/benchmark/445.gobmk/exe/gobmk_base.qemurio --quiet --mode gtp <trevord.tst',
     },
    {'name': '456.hmmer',
     'index': 1,
     'type': 'int',
     'dir': '/benchmark/456.hmmer/run/run_base_ref_qemurio.0000',
     'cmd': '/benchmark/456.hmmer/exe/hmmer_base.qemurio nph3.hmm swiss41',
     },
    {'name': '456.hmmer',
     'index': 2,
     'type': 'int',
     'dir': '/benchmark/456.hmmer/run/run_base_ref_qemurio.0000',
     'cmd': '/benchmark/456.hmmer/exe/hmmer_base.qemurio --fixed 0 --mean 500 --num 500000 --sd 350 --seed 0 retro.hmm',
     },
    {'name': '458.sjeng',
     'index': 1,
     'type': 'int',
     'dir': '/benchmark/458.sjeng/run/run_base_ref_qemurio.0000',
     'cmd': '/benchmark/458.sjeng/exe/sjeng_base.qemurio ref.txt',
     },
    {'name': '462.libquantum',
     'index': 1,
     'type': 'int',
     'dir': '/benchmark/462.libquantum/run/run_base_ref_qemurio.0000',
     'cmd': '/benchmark/462.libquantum/exe/libquantum_base.qemurio 1397 8',
     },
    {'name': '464.h264ref',
     'index': 1,
     'type': 'int',
     'dir': '/benchmark/464.h264ref/run/run_base_ref_qemurio.0000',
     'cmd': '/benchmark/464.h264ref/exe/h264ref_base.qemurio -d foreman_ref_encoder_baseline.cfg',
     },
    {'name': '464.h264ref',
     'index': 2,
     'type': 'int',
     'dir': '/benchmark/464.h264ref/run/run_base_ref_qemurio.0000',
     'cmd': '/benchmark/464.h264ref/exe/h264ref_base.qemurio -d foreman_ref_encoder_main.cfg',
     },
    {'name': '464.h264ref',
     'index': 3,
     'type': 'int',
     'dir': '/benchmark/464.h264ref/run/run_base_ref_qemurio.0000',
     'cmd': '/benchmark/464.h264ref/exe/h264ref_base.qemurio -d sss_encoder_main.cfg',
     },
    {'name': '471.omnetpp',
     'index': 1,
     'type': 'int',
     'dir': '/benchmark/471.omnetpp/run/run_base_ref_qemurio.0000',
     'cmd': '/benchmark/471.omnetpp/exe/omnetpp_base.qemurio omnetpp.ini',
     },
    {'name': '473.astar',
     'index': 1,
     'type': 'int',
     'dir': '/benchmark/473.astar/run/run_base_ref_qemurio.0000',
     'cmd': '/benchmark/473.astar/exe/astar_base.qemurio BigLakes2048.cfg',
     },
    {'name': '473.astar',
     'index': 2,
     'type': 'int',
     'dir': '/benchmark/473.astar/run/run_base_ref_qemurio.0000',
     'cmd': '/benchmark/473.astar/exe/astar_base.qemurio rivers.cfg',
     },
    {'name': '483.xalancbmk',
     'index': 1,
     'type': 'int',
     'dir': '/benchmark/483.xalancbmk/run/run_base_ref_qemurio.0000',
     'cmd': '/benchmark/483.xalancbmk/exe/Xalan_base.qemurio -v t5.xml xalanc.xsl',
     }
]


def start_qemu():
    qemu_cmd = QEMU_COMMAND
    logging.info(qemu_cmd)
    child = pexpect.spawn('bash', ['-c', qemu_cmd], timeout=TIMEOUT)
    index = child.expect(["Please press Enter to activate this console."])
    if (index == 0):
        child.send('\n')
        child.expect(["#"])
        logging.info('qemu started.')
        return child
    else:
        logging.info("start qemu failed.")
        quit_qemu(child)
        return None


def quit_qemu(child):
    child.sendcontrol('a')
    child.send('x')
    logging.info('quit from qemu')


def start_qgem5(input_dir, outdir, cmd, options):
    os.chdir(input_dir)
    command = 'time ' + GEM5_COMMAND.format(outdir, cmd, options)
    child = pexpect.spawn('bash', ['-c', command], timeout=TIMEOUT)
    logging.info('gem5 started.')
    logging.info(command)
    return child


def quit_gem5(child):
    child.close()
    logging.info('quit from rio')


def start_app(qchild, bench):
    qchild.sendline("cd " + bench['dir'])
    qchild.expect('#')
    qchild.sendline('/qrtag -p "' + bench['cmd'] + '"')
    logging.info('app started.')
    logging.info('/qrtag -p "' + bench['cmd'] + '"')


def check_qemu(child):
    logging.info('check qemu')
    child.expect("# ", timeout=TIMEOUT)
    output = child.before
    logging.info(
        "\n qemu cmd output------------------------\n" + child.before + "\n qemu output end------------------------")
    return 'into outreg_end_callback' in output


def check_gem5(child):
    logging.info('check gem5.')
    index = child.expect(pexpect.EOF, timeout=TIMEOUT)
    logging.info(
        "\n gem5 cmd output------------------------\n" + child.before + "\n rio output end------------------------")
    return index == 0


def qgem5(benchmarks):
    for bench in benchmarks:
        qchild = start_qemu()
        logging.info(bench['name'] + " running. ")
        start_app(qchild, bench)
        time.sleep(1)
        rchild = start_qgem5(
            benchmark_base_dir + bench['dir'],
            OUT_PATH + 'qgem5-' + bench['name'] + "-" + str(bench['index']) + '.m5out',
            benchmark_base_dir + bench['cmd'].split(" ", 1)[0],
            bench['cmd'].split(" ", 1)[1] if len(bench['cmd'].split(" ", 1)) > 1 else ''
        )
        if check_qemu(qchild) and check_gem5(rchild):
            quit_gem5(rchild)
        else:
            logging.error("execute " + bench['name'] + "failed. ")
            quit_qemu(qchild)
            quit_gem5(rchild)
            exit()
        logging.info(bench['name'] + " finished.")
        quit_qemu(qchild)
    logging.info("all benchmark finished!")


def qemu(benchmarks):
    for bench in benchmarks:
        qchild = start_qemu()
        logging.info(bench['name'] + " running.")
        start = time.time()
        start_app(qchild, bench)
        qchild.expect("# ")
        logging.info(
            "\n qemu cmd output------------------------\n" + qchild.before + "\n qemu output end------------------------")
        end = time.time()
        m, s = divmod(end - start, 60)
        h, m = divmod(m, 60)
        logging.info(bench['name'] + " finished. run time: %02dh%02dm%02ds" % (h, m, s))
        time.sleep(1)
        quit_qemu(qchild)
    logging.info("all benchmark finished!")


def gem5(benchmarks):
    for bench in benchmarks:
        cd_cmd = "cd " + benchmark_base_dir + bench['dir']
        gem5_run_spec_cmd = GEM5_COMMAND.format(
            OUT_PATH + 'gem5-' + bench['name'] + "-" + str(bench['index']) + '.m5out',
            benchmark_base_dir + bench['cmd'].split(" ", 1)[0],
            bench['cmd'].split(" ", 1)[1] if len(bench['cmd'].split(" ", 1)) > 1 else '',
            bench['name'] + "-" + str(bench['index'])
        )
        logging.info(cd_cmd + " && " + gem5_run_spec_cmd)
        os.system(cd_cmd + " && " + gem5_run_spec_cmd)
        time.sleep(3)

    logging.info("all benchmark started!")


def get_benchmark(benchmark_type, benchmark, benchmark_index):
    if benchmark_type == 'ref':
        bench_to_run = ALL_REF_BENCHMARKS
    elif args.benchmark_type == 'test':
        bench_to_run = ALL_TEST_BENCHMARKS
    else:
        logging.error("must have arg benchmark_type, 'ref' or 'test'")
        bench_to_run = []
    if benchmark:
        benchmarks_list = args.benchmark.split(',')
        bench_to_run = [bench for bench in bench_to_run if bench['name'].split('.')[0] in benchmarks_list]
    if benchmark_index:
        bench_to_run = [bench for bench in bench_to_run if bench['index'] == args.benchmark_index]
    return bench_to_run


if __name__ == '__main__':
    benchmarks_to_run = get_benchmark(args.benchmark_type, args.benchmark, args.benchmark_index)
    logging.info("all benchmarks to run: \n" + json.dumps(benchmarks_to_run, indent=2))
    if args.mode == 'qemu':
        qemu(benchmarks_to_run)
    elif args.mode == 'gem5':
        gem5(benchmarks_to_run)
    elif args.mode == 'qgem5':
        qgem5(benchmarks_to_run)
