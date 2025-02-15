# This file is part of PySFD.
#
# Copyright (c) 2018 Sebastian Stolzenberg,
# Computational Molecular Biology Group,
# Freie Universitaet Berlin (GER)
#
# for any feedback or questions, please contact the author:
# Sebastian Stolzenberg <ss629@cornell.edu>
#
# PySFD is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
#
# PyMOL_VisFeatDiffs_distance_regions
#
from pymol import cmd, stored
import os
#VisFeatDiffsDir = os.environ['PYSFDPATH'] + "/VisFeatDiffs/PyMOL"
VisFeatDiffsDir = "VisFeatDiffs/PyMOL"
cmd.do("run %s/PyMOL_VisFeatDiffs.py" % (VisFeatDiffsDir))

class PyMOL_VisFeatDiffs_distance(PyMOL_VisFeatDiffs):
    '''
    * linewidth            : float, default 5
                             width of lines representing pairwise feature differences
    '''
    __doc__ = PyMOL_VisFeatDiffs.__doc__ + __doc__

    def __init__(self, l_SDApair, l_SDA_not_pair, feature_func_name, stattype, nsigma, nfunit, intrajformat, df_rgn_seg_res_bb=None, VisFeatDiffsDir=None, outdir=None, myview=None, linewidth=5):
        super(PyMOL_VisFeatDiffs_distance, self).__init__(l_SDApair,
                                             l_SDA_not_pair,
                                             feature_func_name,
                                             stattype,
                                             nsigma,
                                             nfunit,
                                             intrajformat,
                                             df_rgn_seg_res_bb,
                                             VisFeatDiffsDir,
                                             outdir,
                                             myview)
        self.linewidth = linewidth     
 
    def _add_vis(self, mymol, row, l_cgo):
        mycolind = int((np.sign(row.sdiff) + 1) / 2)
        if self.df_rgn_seg_res_bb is None:
            if not hasattr(row,"seg1"):
                raise ValueError("row has no column \"rgn1\", but self.df_rgn_seg_res_bb is None - maybe parameter \"coarse_grain_type\" is not properly set?")
            cmd.select("sel1","/%s/%s and i. %d and name ca" % (mymol, row.seg1, row.res1))
            cmd.select("sel2","/%s/%s and i. %d and name ca" % (mymol, row.seg2, row.res2))
        else:
            if not hasattr(row,"rgn1"):
                raise ValueError("row has no column \"rgn1\", but self.df_rgn_seg_res_bb is not None - maybe parameter \"coarse_grain_type\" is not properly set?")
            df_unique_rgnsegbb = self.df_rgn_seg_res_bb[["seg"]].drop_duplicates()
            for myrgn in [row.rgn1, row.rgn2]:
                selstr = "/%s and (" % (mymol)
                for sindex, srow in df_unique_rgnsegbb.iterrows():
                    df_sel = self.df_rgn_seg_res_bb.query("rgn == '%s' and seg == '%s'" % (myrgn, srow.seg))
                    if df_sel.shape[0] > 0:
                        selstr += "(c. %s and i. %s) or" % (srow.seg,
                                                            "+".join([str(x) for x in df_sel.res.values[0]]))
                selstr = selstr[:-3] + ")"
                cmd.select("%s" % myrgn, selstr)
            cmd.set_name("%s" % row.rgn1, "sel1")
            cmd.set_name("%s" % row.rgn2, "sel2")

        count1 = cmd.count_atoms("sel1")
        count2 = cmd.count_atoms("sel2")
        if 0 in [count1, count2]:
            raise ValueError("ZeroCount: count(%s.%d.%s.ca): %d, count(%s.%d.%s.ca): %d" % (row.seg1, row.res1, row.rnm1, count1, row.seg2, row.res2, row.rnm2, count2))
        else:
            com("sel1",state=1)
            #cmd.color(self.sgn2col[mycolind], "sel1")
            coord1=cmd.get_model("sel1_COM",state=1).atom[0].coord
            cmd.delete("sel1_COM")
            com("sel2",state=1)
            #cmd.color(self.sgn2col[mycolind], "sel2")
            coord2=cmd.get_model("sel2_COM",state=1).atom[0].coord
            cmd.delete("sel2_COM")
            l_cgo += [ \
                LINEWIDTH, self.linewidth, \
                BEGIN, LINES, \
                COLOR, self.l_r[mycolind], self.l_g[mycolind], self.l_b[mycolind], \
                VERTEX,   coord1[0], coord1[1],coord1[2], \
                VERTEX,   coord2[0], coord2[1],coord2[2], \
                END \
            ]
            cmd.show("sticks", "sel1")
            cmd.show("sticks", "sel2")
        cmd.delete("sel1")
        cmd.delete("sel2")


#l_SDApair, l_SDA_not_pair: two lists defining what ensembles to compare,
#                           see examples below:
#    # show significant differences between ensembles 'bN82A.pcca2' and 'WT.pcca2'
#    l_SDApair            = [('bN82A.pcca2', 'WT.pcca2')]
#    l_SDA_not_pair       = []
#
#    # show significant differences between ensembles 'bN82A.pcca2' and 'WT.pcca2' ...
#    l_SDApair            = [('bN82A.pcca2', 'WT.pcca2')]
#    # ... which are not significantly different between 'aT41A.pcca1' and 'WT.pcca2'
#    l_SDApair            = [('aT41A.pcca1', 'WT.pcca2')]
#    
#    # show significant differences common to multiple ensemble comparisons ...
#    l_SDApair            = [('bN82A.pcca2', 'WT.pcca2'), ('aT41A.pcca1', 'WT.pcca2')]
#    # ... which are not significantly different among the following comparisons
#    l_SDA_not_pair            = [('aT41A.pcca1', 'bN82A.pcca2')]
l_SDApair            = [('bN82A.pcca2', 'WT.pcca2')]
l_SDA_not_pair       = []

feature_func_name    = "prf.distance.Ca2Ca.std_dev"
coarse_grain_type    = None
stattype             = "samplebatches"
nsigma               = 2.000000
nfunit               = 0.000000
intrajformat         = "xtc"
# output path, currently not used in PyMOL:
outdir               = None

# if called directly from PySFD.view_feature_diffs(),
# update the above parameters:
if 'd_locals' in locals():
    locals().update(d_locals)

if coarse_grain_type is None:
    df_rgn_seg_res_bb = None
elif coarse_grain_type == "cg_nobb":
    df_rgn_seg_res_bb     = pd.read_csv("scripts/df_rgn_seg_res_bb.dat", sep = "\t")
    df_rgn_seg_res_bb.res = df_rgn_seg_res_bb.res.apply(lambda x : list(eval(x)))
elif coarse_grain_type == "cg_withbb":
    df_rgn_seg_res_bb     = pd.read_csv("scripts/df_rgn_seg_res_bb_with_bb.dat", sep = "\t")
    df_rgn_seg_res_bb.res = df_rgn_seg_res_bb.res.apply(lambda x : list(eval(x)))
else:
    raise ValueError("unrecognized value for parameter \"coarse_grain_type:\n%s" % coarse_grain_type)

MyVis = PyMOL_VisFeatDiffs_distance( l_SDApair, l_SDA_not_pair, feature_func_name, stattype, nsigma, nfunit, intrajformat, df_rgn_seg_res_bb=df_rgn_seg_res_bb, VisFeatDiffsDir=VisFeatDiffsDir, outdir=outdir, myview=None)
MyVis.vis_feature_diffs()
