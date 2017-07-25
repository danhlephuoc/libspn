#!/usr/bin/env python3

# ------------------------------------------------------------------------
# Copyright (C) 2016 Andrzej Pronobis - All Rights Reserved
#
# This file is part of LibSPN. Unauthorized use or copying of this file,
# via any medium is strictly prohibited. Proprietary and confidential.
# ------------------------------------------------------------------------

import unittest
import tensorflow as tf
import numpy as np
from context import libspn as spn


class TestNodesParallelSums(unittest.TestCase):

    def tearDown(self):
        tf.reset_default_graph()

    def test_compute_marginal_value(self):
        """Calculating marginal value of Sum."""
        def test(values, num_sums, ivs, weights, feed, output):
            with self.subTest(values=values, num_sums=num_sums, ivs=ivs,
                              weights=weights, feed=feed):
                n = spn.ParallelSums(*values, num_sums=num_sums, ivs=ivs)
                n.generate_weights(weights)
                op = n.get_value(spn.InferenceType.MARGINAL)
                op_log = n.get_log_value(spn.InferenceType.MARGINAL)
                with tf.Session() as sess:
                    spn.initialize_weights(n).run()
                    out = sess.run(op, feed_dict=feed)
                    out_log = sess.run(tf.exp(op_log), feed_dict=feed)

                np.testing.assert_array_almost_equal(
                    out,
                    np.array(output, dtype=spn.conf.dtype.as_numpy_dtype()))
                np.testing.assert_array_almost_equal(
                    out_log,
                    np.array(output, dtype=spn.conf.dtype.as_numpy_dtype()))

        # Create inputs
        v1 = spn.ContVars(num_vars=2, name="ContVars1")
        v2 = spn.ContVars(num_vars=2, name="ContVars2")

        # MULTIPLE PARALLEL-SUM NODES
        # ---------------------------
        num_sums = 2

        # Multiple inputs, multi-element batch
        ivs = spn.IVs(num_vars=num_sums, num_vals=4)

        test([v1, v2],
             num_sums,
             None,
             [0.2, 0.2, 0.3, 0.3, 0.1, 0.2, 0.3, 0.4],
             {v1: [[0.1, 0.2],
                   [0.11, 0.12]],
              v2: [[0.3, 0.4],
                   [0.13, 0.14]]},
             [[(0.1*0.2 + 0.2*0.2 + 0.3*0.3 + 0.4*0.3),
               (0.1*0.1 + 0.2*0.2 + 0.3*0.3 + 0.4*0.4)],
              [(0.11*0.2 + 0.12*0.2 + 0.13*0.3 + 0.14*0.3),
               (0.11*0.1 + 0.12*0.2 + 0.13*0.3 + 0.14*0.4)]])

        test([(v1, [1]), (v2, [0])],
             num_sums,
             None,
             [0.4, 0.6, 0.2, 0.8],
             {v1: [[0.1, 0.2],
                   [0.11, 0.12]],
              v2: [[0.3, 0.4],
                   [0.13, 0.14]]},
             [[(0.2*0.4 + 0.3*0.6), (0.2*0.2 + 0.3*0.8)],
              [(0.12*0.4 + 0.13*0.6), (0.12*0.2 + 0.13*0.8)]])

        test([v1, v2],
             num_sums,
             ivs,
             [0.2, 0.2, 0.3, 0.3, 0.1, 0.2, 0.3, 0.4],
             {v1: [[0.1, 0.2],
                   [0.11, 0.12]],
              v2: [[0.3, 0.4],
                   [0.13, 0.14]],
              ivs: [[-1, -1],
                    [-1, -1]]},
             [[(0.1*0.2 + 0.2*0.2 + 0.3*0.3 + 0.4*0.3),
               (0.1*0.1 + 0.2*0.2 + 0.3*0.3 + 0.4*0.4)],
              [(0.11*0.2 + 0.12*0.2 + 0.13*0.3 + 0.14*0.3),
               (0.11*0.1 + 0.12*0.2 + 0.13*0.3 + 0.14*0.4)]])

        test([v1, v2],
             num_sums,
             ivs,
             [0.2, 0.2, 0.3, 0.3, 0.1, 0.2, 0.3, 0.4],
             {v1: [[0.1, 0.2],
                   [0.11, 0.12]],
              v2: [[0.3, 0.4],
                   [0.13, 0.14]],
              ivs: [[-1, 2],
                    [1, -1]]},
             [[(0.1*0.2 + 0.2*0.2 + 0.3*0.3 + 0.4*0.3), (0.3*0.3)],
              [(0.12*0.2), (0.11*0.1 + 0.12*0.2 + 0.13*0.3 + 0.14*0.4)]])

        test([v1, v2],
             num_sums,
             ivs,
             [0.2, 0.2, 0.3, 0.3, 0.1, 0.2, 0.3, 0.4],
             {v1: [[0.1, 0.2],
                   [0.11, 0.12]],
              v2: [[0.3, 0.4],
                   [0.13, 0.14]],
              ivs: [[3, 2],
                    [0, 1]]},
             [[(0.4*0.3), (0.3*0.3)],
              [(0.11*0.2), (0.12*0.2)]])

        test([(v1, [0, 1]), (v2, [1, 0])],
             num_sums,
             ivs,
             [0.2, 0.2, 0.3, 0.3, 0.1, 0.2, 0.3, 0.4],
             {v1: [[0.1, 0.2],
                   [0.11, 0.12]],
              v2: [[0.3, 0.4],
                   [0.13, 0.14]],
              ivs: [[3, 2],
                    [0, 1]]},
             [[(0.3*0.3), (0.4*0.3)],
              [(0.11*0.2), (0.12*0.2)]])

        # Single input with 1 value, multi-element batch
        ivs = spn.IVs(num_vars=num_sums, num_vals=2)

        test([v1],
             num_sums,
             None,
             [0.4, 0.6, 0.2, 0.8],
             {v1: [[0.1, 0.2],
                   [0.11, 0.12]]},
             [[(0.1*0.4 + 0.2*0.6), (0.1*0.2 + 0.2*0.8)],
              [(0.11*0.4 + 0.12*0.6), (0.11*0.2 + 0.12*0.8)]])

        test([v1],
             num_sums,
             ivs,
             [0.4, 0.6, 0.2, 0.8],
             {v1: [[0.1, 0.2],
                   [0.11, 0.12]],
             ivs: [[-1, -1],
                   [-1, -1]]},
             [[(0.1*0.4 + 0.2*0.6), (0.1*0.2 + 0.2*0.8)],
              [(0.11*0.4 + 0.12*0.6), (0.11*0.2 + 0.12*0.8)]])

        test([v1],
             num_sums,
             ivs,
             [0.4, 0.6, 0.2, 0.8],
             {v1: [[0.1, 0.2],
                   [0.11, 0.12]],
             ivs: [[1, -1],
                   [-1, 0]]},
             [[(0.2*0.6), (0.1*0.2 + 0.2*0.8)],
              [(0.11*0.4 + 0.12*0.6), (0.11*0.2)]])

        test([v1],
             num_sums,
             ivs,
             [0.4, 0.6, 0.2, 0.8],
             {v1: [[0.1, 0.2],
                   [0.11, 0.12]],
             ivs: [[0, 1],
                   [1, 0]]},
             [[(0.1*0.4), (0.2*0.8)],
              [(0.12*0.6), (0.11*0.2)]])

        # Multiple inputs, single-element batch
        ivs = spn.IVs(num_vars=num_sums, num_vals=4)

        test([v1, v2],
             num_sums,
             None,
             [0.2, 0.2, 0.3, 0.3, 0.1, 0.2, 0.3, 0.4],
             {v1: [[0.1, 0.2]],
              v2: [[0.3, 0.4]]},
             [[(0.1*0.2 + 0.2*0.2 + 0.3*0.3 + 0.4*0.3),
               (0.1*0.1 + 0.2*0.2 + 0.3*0.3 + 0.4*0.4)]])

        test([v1, v2],
             num_sums,
             ivs,
             [0.2, 0.2, 0.3, 0.3, 0.1, 0.2, 0.3, 0.4],
             {v1: [[0.1, 0.2]],
              v2: [[0.3, 0.4]],
              ivs: [[-1, -1]]},
             [[(0.1*0.2 + 0.2*0.2 + 0.3*0.3 + 0.4*0.3),
               (0.1*0.1 + 0.2*0.2 + 0.3*0.3 + 0.4*0.4)]])

        test([v1, v2],
             num_sums,
             ivs,
             [0.2, 0.2, 0.3, 0.3, 0.1, 0.2, 0.3, 0.4],
             {v1: [[0.1, 0.2]],
              v2: [[0.3, 0.4]],
              ivs: [[2, -1]]},
             [[(0.3*0.3), (0.1*0.1 + 0.2*0.2 + 0.3*0.3 + 0.4*0.4)]])

        test([v1, v2],
             num_sums,
             ivs,
             [0.2, 0.2, 0.3, 0.3, 0.1, 0.2, 0.3, 0.4],
             {v1: [[0.1, 0.2]],
              v2: [[0.3, 0.4]],
              ivs: [[3, 2]]},
             [[(0.4*0.3), (0.3*0.3)]])

        # Single input with 1 value, single-element batch
        ivs = spn.IVs(num_vars=num_sums, num_vals=2)

        test([v1],
             num_sums,
             None,
             [0.4, 0.6, 0.2, 0.8],
             {v1: [[0.1, 0.2]]},
             [[(0.1*0.4 + 0.2*0.6), (0.1*0.2 + 0.2*0.8)]])

        test([v1],
             num_sums,
             ivs,
             [0.4, 0.6, 0.2, 0.8],
             {v1: [[0.1, 0.2]],
             ivs: [[-1, -1]]},
             [[(0.1*0.4 + 0.2*0.6), (0.1*0.2 + 0.2*0.8)]])

        test([v1],
             num_sums,
             ivs,
             [0.4, 0.6, 0.2, 0.8],
             {v1: [[0.1, 0.2]],
             ivs: [[1, -1]]},
             [[(0.2*0.6), (0.1*0.2 + 0.2*0.8)]])

        test([v1],
             num_sums,
             ivs,
             [0.4, 0.6, 0.2, 0.8],
             {v1: [[0.1, 0.2]],
             ivs: [[0, 1]]},
             [[(0.1*0.4), (0.2*0.8)]])

        # SINGLE PARALLEL-SUM NODE
        # ------------------------
        num_sums = 1

        # Multiple inputs, multi-element batch
        ivs = spn.IVs(num_vars=num_sums, num_vals=4)

        test([v1, v2],
             num_sums,
             None,
             [0.2, 0.2, 0.3, 0.3],
             {v1: [[0.1, 0.2],
                   [0.11, 0.12]],
              v2: [[0.3, 0.4],
                   [0.13, 0.14]]},
             [[(0.1*0.2 + 0.2*0.2 + 0.3*0.3 + 0.4*0.3)],
              [(0.11*0.2 + 0.12*0.2 + 0.13*0.3 + 0.14*0.3)]])

        test([v1, v2],
             num_sums,
             ivs,
             [0.2, 0.2, 0.3, 0.3],
             {v1: [[0.1, 0.2],
                   [0.11, 0.12]],
              v2: [[0.3, 0.4],
                   [0.13, 0.14]],
              ivs: [[-1],
                    [-1]]},
             [[(0.1*0.2 + 0.2*0.2 + 0.3*0.3 + 0.4*0.3)],
              [(0.11*0.2 + 0.12*0.2 + 0.13*0.3 + 0.14*0.3)]])

        test([v1, v2],
             num_sums,
             ivs,
             [0.2, 0.2, 0.3, 0.3],
             {v1: [[0.1, 0.2],
                   [0.11, 0.12]],
              v2: [[0.3, 0.4],
                   [0.13, 0.14]],
              ivs: [[-1],
                    [3]]},
             [[(0.1*0.2 + 0.2*0.2 + 0.3*0.3 + 0.4*0.3)],
              [(0.14*0.3)]])

        test([v1, v2],
             num_sums,
             ivs,
             [0.2, 0.2, 0.3, 0.3],
             {v1: [[0.1, 0.2],
                   [0.11, 0.12]],
              v2: [[0.3, 0.4],
                   [0.13, 0.14]],
              ivs: [[3],
                    [0]]},
             [[(0.4*0.3)],
              [(0.11*0.2)]])

        # Single input with 1 value, multi-element batch
        ivs = spn.IVs(num_vars=num_sums, num_vals=2)

        test([v1],
             num_sums,
             None,
             [0.4, 0.6],
             {v1: [[0.1, 0.2],
                   [0.11, 0.12]]},
             [[0.1*0.4 + 0.2*0.6],
              [0.11*0.4 + 0.12*0.6]])

        test([v1],
             num_sums,
             ivs,
             [0.4, 0.6],
             {v1: [[0.1, 0.2],
                   [0.11, 0.12]],
             ivs: [[-1],
                   [-1]]},
             [[0.1*0.4 + 0.2*0.6],
              [0.11*0.4 + 0.12*0.6]])

        test([v1],
             num_sums,
             ivs,
             [0.4, 0.6],
             {v1: [[0.1, 0.2],
                   [0.11, 0.12]],
             ivs: [[1],
                   [-1]]},
             [[0.2*0.6],
              [0.11*0.4 + 0.12*0.6]])

        test([v1],
             num_sums,
             ivs,
             [0.4, 0.6],
             {v1: [[0.1, 0.2],
                   [0.11, 0.12]],
             ivs: [[0],
                   [1]]},
             [[0.1*0.4],
              [0.12*0.6]])

        # Multiple inputs, single-element batch
        ivs = spn.IVs(num_vars=num_sums, num_vals=4)

        test([v1, v2],
             num_sums,
             None,
             [0.2, 0.2, 0.3, 0.3],
             {v1: [[0.1, 0.2]],
              v2: [[0.3, 0.4]]},
             [[0.1*0.2 + 0.2*0.2 + 0.3*0.3 + 0.4*0.3]])

        test([v1, v2],
             num_sums,
             ivs,
             [0.2, 0.2, 0.3, 0.3],
             {v1: [[0.1, 0.2]],
              v2: [[0.3, 0.4]],
              ivs: [[-1]]},
             [[0.1*0.2 + 0.2*0.2 + 0.3*0.3 + 0.4*0.3]])

        test([v1, v2],
             num_sums,
             ivs,
             [0.1, 0.2, 0.3, 0.4],
             {v1: [[0.1, 0.2]],
              v2: [[0.3, 0.4]],
              ivs: [[2]]},
             [[0.3*0.3]])

        # Single input with 1 value, single-element batch
        ivs = spn.IVs(num_vars=num_sums, num_vals=2)

        test([v1],
             num_sums,
             None,
             [0.4, 0.6],
             {v1: [[0.1, 0.2]]},
             [[0.1*0.4 + 0.2*0.6]])

        test([v1],
             num_sums,
             ivs,
             [0.2, 0.8],
             {v1: [[0.1, 0.2]],
             ivs: [[-1]]},
             [[0.1*0.2 + 0.2*0.8]])

        test([v1],
             num_sums,
             ivs,
             [0.2, 0.8],
             {v1: [[0.1, 0.2]],
             ivs: [[1]]},
             [[0.2*0.8]])

    def test_compute_mpe_value(self):
        """Calculating MPE value of Parallel Sums."""
        def test(values, num_sums, ivs, weights, feed, output):
            with self.subTest(values=values, num_sums=num_sums, ivs=ivs,
                              weights=weights, feed=feed):
                n = spn.ParallelSums(*values, num_sums=num_sums, ivs=ivs)
                n.generate_weights(weights)
                op = n.get_value(spn.InferenceType.MPE)
                op_log = n.get_log_value(spn.InferenceType.MPE)
                with tf.Session() as sess:
                    spn.initialize_weights(n).run()
                    out = sess.run(op, feed_dict=feed)
                    out_log = sess.run(tf.exp(op_log), feed_dict=feed)

                np.testing.assert_array_almost_equal(
                    out,
                    np.array(output, dtype=spn.conf.dtype.as_numpy_dtype()))
                np.testing.assert_array_almost_equal(
                    out_log,
                    np.array(output, dtype=spn.conf.dtype.as_numpy_dtype()))

        # Create inputs
        v1 = spn.ContVars(num_vars=2, name="ContVars1")
        v2 = spn.ContVars(num_vars=2, name="ContVars2")

        # MULTIPLE PARALLEL-SUM NODES
        # ---------------------------
        num_sums = 2

        # Multiple inputs, multi-element batch
        ivs = spn.IVs(num_vars=num_sums, num_vals=4)

        test([v1, v2],
             num_sums,
             None,
             [0.2, 0.2, 0.3, 0.3, 0.1, 0.2, 0.3, 0.4],
             {v1: [[0.1, 0.2],
                   [0.11, 0.12]],
              v2: [[0.3, 0.4],
                   [0.13, 0.14]]},
             [[(0.4*0.3), (0.4*0.4)],
              [(0.14*0.3), (0.14*0.4)]])

        test([v1, v2],
             num_sums,
             ivs,
             [0.3, 0.3, 0.2, 0.2, 0.4, 0.3, 0.2, 0.1],
             {v1: [[0.1, 0.2],
                   [0.11, 0.12]],
              v2: [[0.3, 0.4],
                   [0.13, 0.14]],
              ivs: [[-1, -1],
                    [-1, -1]]},
             [[(0.4*0.2), (0.3*0.2)],
              [(0.12*0.3), (0.11*0.4)]])

        test([v1, v2],
             num_sums,
             ivs,
             [0.2, 0.2, 0.3, 0.3, 0.1, 0.2, 0.3, 0.4],
             {v1: [[0.1, 0.2],
                   [0.11, 0.12]],
              v2: [[0.3, 0.4],
                   [0.13, 0.14]],
              ivs: [[-1, 2],
                    [1, -1]]},
             [[(0.4*0.3), (0.3*0.3)],
              [(0.12*0.2), (0.14*0.4)]])

        test([v1, v2],
             num_sums,
             ivs,
             [0.2, 0.2, 0.3, 0.3, 0.1, 0.2, 0.3, 0.4],
             {v1: [[0.1, 0.2],
                   [0.11, 0.12]],
              v2: [[0.3, 0.4],
                   [0.13, 0.14]],
              ivs: [[3, 2],
                    [0, 1]]},
             [[(0.4*0.3), (0.3*0.3)],
              [(0.11*0.2), (0.12*0.2)]])

        # Single input with 1 value, multi-element batch
        ivs = spn.IVs(num_vars=num_sums, num_vals=2)

        test([v1],
             num_sums,
             None,
             [0.4, 0.6, 0.8, 0.2],
             {v1: [[0.1, 0.2],
                   [0.11, 0.12]]},
             [[(0.2*0.6), (0.1*0.8)],
              [(0.12*0.6), (0.11*0.8)]])

        test([v1],
             num_sums,
             ivs,
             [0.6, 0.4, 0.2, 0.8],
             {v1: [[0.1, 0.2],
                   [0.11, 0.12]],
             ivs: [[-1, -1],
                   [-1, -1]]},
             [[(0.2*0.4), (0.2*0.8)],
              [(0.11*0.6), (0.12*0.8)]])

        test([v1],
             num_sums,
             ivs,
             [0.4, 0.6, 0.2, 0.8],
             {v1: [[0.1, 0.2],
                   [0.11, 0.12]],
             ivs: [[1, -1],
                   [-1, 0]]},
             [[(0.2*0.6), (0.2*0.8)],
              [(0.12*0.6), (0.11*0.2)]])

        test([v1],
             num_sums,
             ivs,
             [0.4, 0.6, 0.2, 0.8],
             {v1: [[0.1, 0.2],
                   [0.11, 0.12]],
             ivs: [[0, 1],
                   [1, 0]]},
             [[(0.1*0.4), (0.2*0.8)],
              [(0.12*0.6), (0.11*0.2)]])

        # Multiple inputs, single-element batch
        ivs = spn.IVs(num_vars=num_sums, num_vals=4)

        test([v1, v2],
             num_sums,
             None,
             [0.2, 0.2, 0.3, 0.3, 0.1, 0.2, 0.3, 0.4],
             {v1: [[0.1, 0.2]],
              v2: [[0.3, 0.4]]},
             [[(0.4*0.3), (0.4*0.4)]])

        test([v1, v2],
             num_sums,
             ivs,
             [0.3, 0.3, 0.2, 0.2, 0.4, 0.3, 0.2, 0.1],
             {v1: [[0.1, 0.2]],
              v2: [[0.3, 0.4]],
              ivs: [[-1, -1]]},
             [[(0.4*0.2), (0.2*0.3)]])

        test([v1, v2],
             num_sums,
             ivs,
             [0.2, 0.2, 0.3, 0.3, 0.1, 0.2, 0.3, 0.4],
             {v1: [[0.1, 0.2]],
              v2: [[0.3, 0.4]],
              ivs: [[2, -1]]},
             [[(0.3*0.3), (0.4*0.4)]])

        test([v1, v2],
             num_sums,
             ivs,
             [0.2, 0.2, 0.3, 0.3, 0.1, 0.2, 0.3, 0.4],
             {v1: [[0.1, 0.2]],
              v2: [[0.3, 0.4]],
              ivs: [[3, 2]]},
             [[(0.4*0.3), (0.3*0.3)]])

        # Single input with 1 value, single-element batch
        ivs = spn.IVs(num_vars=num_sums, num_vals=2)

        test([v1],
             num_sums,
             None,
             [0.6, 0.4, 0.2, 0.8],
             {v1: [[0.1, 0.2]]},
             [[(0.2*0.4), (0.2*0.8)]])

        test([v1],
             num_sums,
             ivs,
             [0.4, 0.6, 0.8, 0.2],
             {v1: [[0.1, 0.2]],
             ivs: [[-1, -1]]},
             [[(0.2*0.6), (0.1*0.8)]])

        test([v1],
             num_sums,
             ivs,
             [0.4, 0.6, 0.2, 0.8],
             {v1: [[0.1, 0.2]],
             ivs: [[0, -1]]},
             [[(0.1*0.4), (0.2*0.8)]])

        test([v1],
             num_sums,
             ivs,
             [0.6, 0.4, 0.8, 0.2],
             {v1: [[0.1, 0.2]],
             ivs: [[1, 0]]},
             [[(0.2*0.4), (0.1*0.8)]])

        # SINGLE PARALLEL-SUM NODE
        # ------------------------
        num_sums = 1

        # Multiple inputs, multi-element batch
        ivs = spn.IVs(num_vars=num_sums, num_vals=4)

        test([v1, v2],
             num_sums,
             None,
             [0.2, 0.2, 0.3, 0.3],
             {v1: [[0.1, 0.2],
                   [0.11, 0.12]],
              v2: [[0.3, 0.4],
                   [0.13, 0.14]]},
             [[(0.4*0.3)],
              [(0.14*0.3)]])

        test([v1, v2],
             num_sums,
             ivs,
             [0.4, 0.3, 0.2, 0.1],
             {v1: [[0.1, 0.2],
                   [0.11, 0.12]],
              v2: [[0.3, 0.4],
                   [0.13, 0.14]],
              ivs: [[-1],
                    [-1]]},
             [[(0.3*0.2)],
              [(0.11*0.4)]])

        test([v1, v2],
             num_sums,
             ivs,
             [0.2, 0.2, 0.3, 0.3],
             {v1: [[0.1, 0.2],
                   [0.11, 0.12]],
              v2: [[0.3, 0.4],
                   [0.13, 0.14]],
              ivs: [[-1],
                    [3]]},
             [[(0.4*0.3)],
              [(0.14*0.3)]])

        test([v1, v2],
             num_sums,
             ivs,
             [0.2, 0.2, 0.3, 0.3],
             {v1: [[0.1, 0.2],
                   [0.11, 0.12]],
              v2: [[0.3, 0.4],
                   [0.13, 0.14]],
              ivs: [[3],
                    [0]]},
             [[(0.4*0.3)],
              [(0.11*0.2)]])

        # Single input with 1 value, multi-element batch
        ivs = spn.IVs(num_vars=num_sums, num_vals=2)

        test([v1],
             num_sums,
             None,
             [0.4, 0.6],
             {v1: [[0.1, 0.2],
                   [0.11, 0.12]]},
             [[0.2*0.6],
              [0.12*0.6]])

        test([v1],
             num_sums,
             ivs,
             [0.6, 0.4],
             {v1: [[0.1, 0.2],
                   [0.11, 0.12]],
             ivs: [[-1],
                   [-1]]},
             [[0.2*0.4],
              [0.11*0.6]])

        test([v1],
             num_sums,
             ivs,
             [0.4, 0.6],
             {v1: [[0.1, 0.2],
                   [0.11, 0.12]],
             ivs: [[0],
                   [-1]]},
             [[0.1*0.4],
              [0.12*0.6]])

        test([v1],
             num_sums,
             ivs,
             [0.4, 0.6],
             {v1: [[0.1, 0.2],
                   [0.11, 0.12]],
             ivs: [[1],
                   [0]]},
             [[0.2*0.6],
              [0.11*0.4]])

        # Multiple inputs, single-element batch
        ivs = spn.IVs(num_vars=num_sums, num_vals=4)

        test([v1, v2],
             num_sums,
             None,
             [0.2, 0.2, 0.3, 0.3],
             {v1: [[0.1, 0.2]],
              v2: [[0.3, 0.4]]},
             [[0.4*0.3]])

        test([v1, v2],
             num_sums,
             ivs,
             [0.4, 0.3, 0.2, 0.1],
             {v1: [[0.1, 0.2]],
              v2: [[0.3, 0.4]],
              ivs: [[-1]]},
             [[0.2*0.3]])

        test([v1, v2],
             num_sums,
             ivs,
             [0.1, 0.2, 0.3, 0.4],
             {v1: [[0.1, 0.2]],
              v2: [[0.3, 0.4]],
              ivs: [[2]]},
             [[0.3*0.3]])

        # Single input with 1 value, single-element batch
        ivs = spn.IVs(num_vars=num_sums, num_vals=2)

        test([v1],
             num_sums,
             None,
             [0.4, 0.6],
             {v1: [[0.1, 0.2]]},
             [[0.2*0.6]])

        test([v1],
             num_sums,
             ivs,
             [0.6, 0.4],
             {v1: [[0.1, 0.2]],
             ivs: [[-1]]},
             [[0.2*0.4]])

        test([v1],
             num_sums,
             ivs,
             [0.2, 0.8],
             {v1: [[0.1, 0.2]],
             ivs: [[0]]},
             [[0.1*0.2]])

    def test_comput_scope(self):
        """Calculating scope of ParallelSums"""
        # Create graph
        v12 = spn.IVs(num_vars=2, num_vals=4)
        v34 = spn.ContVars(num_vars=2)
        ivs_s4 = spn.IVs(num_vars=3, num_vals=4)
        s1 = spn.ParallelSums((v12, [0, 1, 2, 3]), num_sums=2)
        s1.generate_ivs()
        s2 = spn.ParallelSums((v12, [4, 5, 6, 7]), num_sums=1)
        p1 = spn.Product((v12, [0, 7]))
        p2 = spn.Product((v12, [3, 4]))
        p3 = spn.Product(v34)
        n1 = spn.Concat(s1, s2, p3)
        n2 = spn.Concat(p1, p2)
        p4 = spn.Product((n1, [0]), (n1, [1]))
        p5 = spn.Product((n2, [0]), (n1, [2]))
        s3 = spn.Sum(p4, n2)
        p6 = spn.Product(s3, (n1, [2]))
        s4 = spn.Sum(p5, p6, ivs=ivs_s4)
        # Test
        self.assertListEqual(v12.get_scope(),
                             [spn.Scope(v12, 0), spn.Scope(v12, 0),
                              spn.Scope(v12, 0), spn.Scope(v12, 0),
                              spn.Scope(v12, 1), spn.Scope(v12, 1),
                              spn.Scope(v12, 1), spn.Scope(v12, 1)])
        self.assertListEqual(v34.get_scope(),
                             [spn.Scope(v34, 0), spn.Scope(v34, 1)])
        self.assertListEqual(s1.get_scope(),
                             [spn.Scope(v12, 0) | spn.Scope(s1.ivs.node, 0) |
                              spn.Scope(s1.ivs.node, 1)])
        self.assertListEqual(s2.get_scope(),
                             [spn.Scope(v12, 1)])
        self.assertListEqual(p1.get_scope(),
                             [spn.Scope(v12, 0) | spn.Scope(v12, 1)])
        self.assertListEqual(p2.get_scope(),
                             [spn.Scope(v12, 0) | spn.Scope(v12, 1)])
        self.assertListEqual(p3.get_scope(),
                             [spn.Scope(v34, 0) | spn.Scope(v34, 1)])
        self.assertListEqual(n1.get_scope(),
                             [spn.Scope(v12, 0) | spn.Scope(s1.ivs.node, 0) |
                              spn.Scope(s1.ivs.node, 1), spn.Scope(v12, 1),
                              spn.Scope(v34, 0) | spn.Scope(v34, 1)])
        self.assertListEqual(n2.get_scope(),
                             [spn.Scope(v12, 0) | spn.Scope(v12, 1),
                              spn.Scope(v12, 0) | spn.Scope(v12, 1)])
        self.assertListEqual(p4.get_scope(),
                             [spn.Scope(v12, 0) | spn.Scope(v12, 1) |
                              spn.Scope(s1.ivs.node, 0) |
                              spn.Scope(s1.ivs.node, 1)])
        self.assertListEqual(p5.get_scope(),
                             [spn.Scope(v12, 0) | spn.Scope(v12, 1) |
                              spn.Scope(v34, 0) | spn.Scope(v34, 1)])
        self.assertListEqual(s3.get_scope(),
                             [spn.Scope(v12, 0) | spn.Scope(v12, 1) |
                              spn.Scope(s1.ivs.node, 0) |
                              spn.Scope(s1.ivs.node, 1)])
        self.assertListEqual(p6.get_scope(),
                             [spn.Scope(v12, 0) | spn.Scope(v12, 1) |
                              spn.Scope(v34, 0) | spn.Scope(v34, 1) |
                              spn.Scope(s1.ivs.node, 0) |
                              spn.Scope(s1.ivs.node, 1)])
        self.assertListEqual(s4.get_scope(),
                             [spn.Scope(v12, 0) | spn.Scope(v12, 1) |
                              spn.Scope(v34, 0) | spn.Scope(v34, 1) |
                              spn.Scope(s1.ivs.node, 0) |
                              spn.Scope(s1.ivs.node, 1) |
                              spn.Scope(s4.ivs.node, 0) |
                              spn.Scope(s4.ivs.node, 1) |
                              spn.Scope(s4.ivs.node, 2)])

    def test_compute_valid(self):
        """Calculating validity of ParallelSums"""
        # Without IVs
        v12 = spn.IVs(num_vars=2, num_vals=4)
        v34 = spn.ContVars(num_vars=2)
        s1 = spn.ParallelSums((v12, [0, 1, 2, 3]), num_sums=3)
        s2 = spn.ParallelSums((v12, [0, 1, 2, 4]), name="S2")
        s3 = spn.ParallelSums((v12, [0, 1, 2, 3]), (v34, 0), num_sums=2)
        p1 = spn.Product((v12, [0, 5]), (v34, 0))
        p2 = spn.Product((v12, [1, 6]), (v34, 0))
        p3 = spn.Product((v12, [1, 6]), (v34, 1))
        s4 = spn.ParallelSums(p1, p2, num_sums=2)
        s5 = spn.ParallelSums(p1, p3, num_sums=3)
        self.assertTrue(v12.is_valid())
        self.assertTrue(v34.is_valid())
        self.assertTrue(s1.is_valid())
        self.assertFalse(s2.is_valid())
        self.assertFalse(s3.is_valid())
        self.assertTrue(s4.is_valid())
        self.assertFalse(s5.is_valid())
        # With IVS
        s6 = spn.ParallelSums(p1, p2, num_sums=3)
        s6.generate_ivs()
        self.assertTrue(s6.is_valid())
        s7 = spn.ParallelSums(p1, p2, num_sums=1)
        s7.set_ivs(spn.ContVars(num_vars=2))
        self.assertFalse(s7.is_valid())
        s8 = spn.ParallelSums(p1, p2, num_sums=2)
        s8.set_ivs(spn.IVs(num_vars=3, num_vals=2))
        s9 = spn.ParallelSums(p1, p2, num_sums=2)
        s9.set_ivs(spn.ContVars(num_vars=2))
        with self.assertRaises(spn.StructureError):
            s8.is_valid()
            s9.is_valid()
        s10 = spn.ParallelSums(p1, p2, num_sums=2)
        s10.set_ivs((v12, [0, 3, 5, 7]))
        self.assertTrue(s10.is_valid())

    def test_compute_mpe_path_noivs_single_sum(self):
        v12 = spn.IVs(num_vars=2, num_vals=4)
        v34 = spn.ContVars(num_vars=2)
        v5 = spn.ContVars(num_vars=1)
        s = spn.ParallelSums((v12, [0, 5]), v34, (v12, [3]), v5)
        w = s.generate_weights()
        counts = tf.placeholder(tf.float32, shape=(None, 1))
        op = s._compute_mpe_path(tf.identity(counts),
                                 w.get_value(),
                                 None,
                                 v12.get_value(),
                                 v34.get_value(),
                                 v12.get_value(),
                                 v5.get_value())
        init = w.initialize()
        counts_feed = [[10],
                       [11],
                       [12],
                       [13]]
        v12_feed = [[0, 1],
                    [1, 1],
                    [0, 0],
                    [3, 3]]
        v34_feed = [[0.1, 0.2],
                    [1.2, 0.2],
                    [0.1, 0.2],
                    [0.9, 0.8]]
        v5_feed = [[0.5],
                   [0.5],
                   [1.2],
                   [0.9]]

        with tf.Session() as sess:
            sess.run(init)
            # Skip the IVs op
            out = sess.run(op[:1] + op[2:], feed_dict={counts: counts_feed,
                                                       v12: v12_feed,
                                                       v34: v34_feed,
                                                       v5: v5_feed})
        # Weights
        np.testing.assert_array_almost_equal(
            out[0], np.transpose(np.array([[[10., 0., 0., 0., 0., 0.],
                                            [0., 0., 11., 0., 0., 0.],
                                            [0., 0., 0., 0., 0., 12.],
                                            [0., 0., 0., 0., 13., 0.]]],
                                 dtype=np.float32), [1, 0, 2]))

        np.testing.assert_array_almost_equal(
            out[1], np.array([[10., 0., 0., 0., 0., 0., 0., 0.],
                              [0., 0., 0., 0., 0., 0., 0., 0.],
                              [0., 0., 0., 0., 0., 0., 0., 0.],
                              [0., 0., 0., 0., 0., 0., 0., 0.]],
                             dtype=np.float32))

        np.testing.assert_array_almost_equal(
            out[2], np.array([[0., 0.],
                              [11., 0.],
                              [0., 0.],
                              [0., 0.]],
                             dtype=np.float32))

        np.testing.assert_array_almost_equal(
            out[3], np.array([[0., 0., 0., 0., 0., 0., 0., 0.],
                              [0., 0., 0., 0., 0., 0., 0., 0.],
                              [0., 0., 0., 0., 0., 0., 0., 0.],
                              [0., 0., 0., 13., 0., 0., 0., 0.]],
                             dtype=np.float32))

        np.testing.assert_array_almost_equal(
            out[4], np.array([[0.],
                              [0.],
                              [12.],
                              [0.]],
                             dtype=np.float32))

    def test_compute_mpe_path_noivs_multi_sums(self):
        v12 = spn.IVs(num_vars=2, num_vals=4)
        v34 = spn.ContVars(num_vars=2)
        v5 = spn.ContVars(num_vars=1)
        s = spn.ParallelSums((v12, [0, 5]), v34, (v12, [3]), v5, num_sums=2)
        w = s.generate_weights()
        counts = tf.placeholder(tf.float32, shape=(None, 2))
        op = s._compute_mpe_path(tf.identity(counts),
                                 w.get_value(),
                                 None,
                                 v12.get_value(),
                                 v34.get_value(),
                                 v12.get_value(),
                                 v5.get_value())
        init = w.initialize()
        counts_feed = [[10, 20],
                       [11, 21],
                       [12, 22],
                       [13, 23]]
        v12_feed = [[0, 1],
                    [1, 1],
                    [0, 0],
                    [3, 3]]
        v34_feed = [[0.1, 0.2],
                    [1.2, 0.2],
                    [0.1, 0.2],
                    [0.9, 0.8]]
        v5_feed = [[0.5],
                   [0.5],
                   [1.2],
                   [0.9]]

        with tf.Session() as sess:
            sess.run(init)
            # Skip the IVs op
            out = sess.run(op[:1] + op[2:], feed_dict={counts: counts_feed,
                                                       v12: v12_feed,
                                                       v34: v34_feed,
                                                       v5: v5_feed})
        # Weights
        np.testing.assert_array_almost_equal(
            out[0], np.transpose(np.array([[[10., 0., 0., 0., 0., 0.],
                                            [0., 0., 11., 0., 0., 0.],
                                            [0., 0., 0., 0., 0., 12.],
                                            [0., 0., 0., 0., 13., 0.]],
                                           [[20., 0., 0., 0., 0., 0.],
                                            [0., 0., 21., 0., 0., 0.],
                                            [0., 0., 0., 0., 0., 22.],
                                            [0., 0., 0., 0., 23., 0.]]],
                                 dtype=np.float32), [1, 0, 2]))

        np.testing.assert_array_almost_equal(
            out[1], np.array([[30., 0., 0., 0., 0., 0., 0., 0.],
                              [0., 0., 0., 0., 0., 0., 0., 0.],
                              [0., 0., 0., 0., 0., 0., 0., 0.],
                              [0., 0., 0., 0., 0., 0., 0., 0.]],
                             dtype=np.float32))

        np.testing.assert_array_almost_equal(
            out[2], np.array([[0., 0.],
                              [32., 0.],
                              [0., 0.],
                              [0., 0.]],
                             dtype=np.float32))

        np.testing.assert_array_almost_equal(
            out[3], np.array([[0., 0., 0., 0., 0., 0., 0., 0.],
                              [0., 0., 0., 0., 0., 0., 0., 0.],
                              [0., 0., 0., 0., 0., 0., 0., 0.],
                              [0., 0., 0., 36., 0., 0., 0., 0.]],
                             dtype=np.float32))

        np.testing.assert_array_almost_equal(
            out[4], np.array([[0.],
                              [0.],
                              [34.],
                              [0.]],
                             dtype=np.float32))

    def test_compute_mpe_path_ivs_single_sum(self):
        v12 = spn.IVs(num_vars=2, num_vals=4)
        v34 = spn.ContVars(num_vars=2)
        v5 = spn.ContVars(num_vars=1)
        s = spn.ParallelSums((v12, [0, 5]), v34, (v12, [3]), v5)
        iv = s.generate_ivs()
        w = s.generate_weights()
        counts = tf.placeholder(tf.float32, shape=(None, 1))
        op = s._compute_mpe_path(tf.identity(counts),
                                 w.get_value(),
                                 iv.get_value(),
                                 v12.get_value(),
                                 v34.get_value(),
                                 v12.get_value(),
                                 v5.get_value())
        init = w.initialize()
        counts_feed = [[10],
                       [11],
                       [12],
                       [13],
                       [14],
                       [15],
                       [16],
                       [17]]
        v12_feed = [[0, 1],
                    [1, 1],
                    [0, 0],
                    [3, 3],
                    [0, 1],
                    [1, 1],
                    [0, 0],
                    [3, 3]]
        v34_feed = [[0.1, 0.2],
                    [1.2, 0.2],
                    [0.1, 0.2],
                    [0.9, 0.8],
                    [0.1, 0.2],
                    [1.2, 0.2],
                    [0.1, 0.2],
                    [0.9, 0.8]]
        v5_feed = [[0.5],
                   [0.5],
                   [1.2],
                   [0.9],
                   [0.5],
                   [0.5],
                   [1.2],
                   [0.9]]
        ivs_feed = [[-1], [-1], [-1], [-1], [1], [2], [3], [1]]

        with tf.Session() as sess:
            sess.run(init)
            out = sess.run(op, feed_dict={counts: counts_feed,
                                          iv: ivs_feed,
                                          v12: v12_feed,
                                          v34: v34_feed,
                                          v5: v5_feed})
        # Weights
        np.testing.assert_array_almost_equal(
            out[0], np.transpose(np.array([[[10., 0., 0., 0., 0., 0.],
                                            [0., 0., 11., 0., 0., 0.],
                                            [0., 0., 0., 0., 0., 12.],
                                            [0., 0., 0., 0., 13., 0.],
                                            [0., 14., 0., 0., 0., 0.],
                                            [0., 0., 15., 0., 0., 0.],
                                            [0., 0., 0., 16., 0., 0.],
                                            [17., 0., 0., 0., 0., 0.]]],
                                 dtype=np.float32), [1, 0, 2]))

        # IVs
        np.testing.assert_array_almost_equal(
            out[1], np.array([[10., 0., 0., 0., 0., 0.],
                              [0., 0., 11., 0., 0., 0.],
                              [0., 0., 0., 0., 0., 12.],
                              [0., 0., 0., 0., 13., 0.],
                              [0., 14., 0., 0., 0., 0.],
                              [0., 0., 15., 0., 0., 0.],
                              [0., 0., 0., 16., 0., 0.],
                              [17., 0., 0., 0., 0., 0.]],
                             dtype=np.float32))

        np.testing.assert_array_almost_equal(
            out[2], np.array([[10., 0., 0., 0., 0., 0., 0., 0.],
                              [0., 0., 0., 0., 0., 0., 0., 0.],
                              [0., 0., 0., 0., 0., 0., 0., 0.],
                              [0., 0., 0., 0., 0., 0., 0., 0.],
                              [0., 0., 0., 0., 0., 14., 0., 0.],
                              [0., 0., 0., 0., 0., 0., 0., 0.],
                              [0., 0., 0., 0., 0., 0., 0., 0.],
                              [17., 0., 0., 0., 0., 0., 0., 0.]],
                             dtype=np.float32))

        np.testing.assert_array_almost_equal(
            out[3], np.array([[0., 0.],
                              [11., 0.],
                              [0., 0.],
                              [0., 0.],
                              [0., 0.],
                              [15., 0.],
                              [0., 16.],
                              [0., 0.]],
                             dtype=np.float32))

        np.testing.assert_array_almost_equal(
            out[4], np.array([[0., 0., 0., 0., 0., 0., 0., 0.],
                              [0., 0., 0., 0., 0., 0., 0., 0.],
                              [0., 0., 0., 0., 0., 0., 0., 0.],
                              [0., 0., 0., 13., 0., 0., 0., 0.],
                              [0., 0., 0., 0., 0., 0., 0., 0.],
                              [0., 0., 0., 0., 0., 0., 0., 0.],
                              [0., 0., 0., 0., 0., 0., 0., 0.],
                              [0., 0., 0., 0., 0., 0., 0., 0.]],
                             dtype=np.float32))

        np.testing.assert_array_almost_equal(
            out[5], np.array([[0.],
                              [0.],
                              [12.],
                              [0.],
                              [0.],
                              [0.],
                              [0.],
                              [0.]],
                             dtype=np.float32))

    def test_compute_mpe_path_ivs_multi_sums(self):
        v12 = spn.IVs(num_vars=2, num_vals=4)
        v34 = spn.ContVars(num_vars=2)
        v5 = spn.ContVars(num_vars=1)
        s = spn.ParallelSums((v12, [0, 5]), v34, (v12, [3]), v5, num_sums=2)
        iv = s.generate_ivs()
        w = s.generate_weights()
        counts = tf.placeholder(tf.float32, shape=(None, 2))
        op = s._compute_mpe_path(tf.identity(counts),
                                 w.get_value(),
                                 iv.get_value(),
                                 v12.get_value(),
                                 v34.get_value(),
                                 v12.get_value(),
                                 v5.get_value())
        init = w.initialize()
        counts_feed = [[10, 20],
                       [11, 21],
                       [12, 22],
                       [13, 23],
                       [14, 24],
                       [15, 25],
                       [16, 26],
                       [17, 27]]
        v12_feed = [[0, 1],
                    [1, 1],
                    [0, 0],
                    [3, 3],
                    [0, 1],
                    [1, 1],
                    [0, 0],
                    [3, 3]]
        v34_feed = [[0.1, 0.2],
                    [1.2, 0.2],
                    [0.1, 0.2],
                    [0.9, 0.8],
                    [0.1, 0.2],
                    [1.2, 0.2],
                    [0.1, 0.2],
                    [0.9, 0.8]]
        v5_feed = [[0.5],
                   [0.5],
                   [1.2],
                   [0.9],
                   [0.5],
                   [0.5],
                   [1.2],
                   [0.9]]
        ivs_feed = [[-1, -1],
                    [-1, -1],
                    [-1, -1],
                    [-1, -1],
                    [1, 1],
                    [2, 2],
                    [3, 3],
                    [1, 1]]

        with tf.Session() as sess:
            sess.run(init)
            out = sess.run(op, feed_dict={counts: counts_feed,
                                          iv: ivs_feed,
                                          v12: v12_feed,
                                          v34: v34_feed,
                                          v5: v5_feed})
        # Weights
        np.testing.assert_array_almost_equal(
            out[0], np.transpose(np.array([[[10., 0., 0., 0., 0., 0.],
                                            [0., 0., 11., 0., 0., 0.],
                                            [0., 0., 0., 0., 0., 12.],
                                            [0., 0., 0., 0., 13., 0.],
                                            [0., 14., 0., 0., 0., 0.],
                                            [0., 0., 15., 0., 0., 0.],
                                            [0., 0., 0., 16., 0., 0.],
                                            [17., 0., 0., 0., 0., 0.]],
                                           [[20., 0., 0., 0., 0., 0.],
                                            [0., 0., 21., 0., 0., 0.],
                                            [0., 0., 0., 0., 0., 22.],
                                            [0., 0., 0., 0., 23., 0.],
                                            [0., 24., 0., 0., 0., 0.],
                                            [0., 0., 25., 0., 0., 0.],
                                            [0., 0., 0., 26., 0., 0.],
                                            [27., 0., 0., 0., 0., 0.]]],
                                 dtype=np.float32), [1, 0, 2]))

        # IVs
        np.testing.assert_array_almost_equal(
            out[1], np.array([[30., 0., 0., 0., 0., 0.],
                              [0., 0., 32., 0., 0., 0.],
                              [0., 0., 0., 0., 0., 34.],
                              [0., 0., 0., 0., 36., 0.],
                              [0., 38., 0., 0., 0., 0.],
                              [0., 0., 40., 0., 0., 0.],
                              [0., 0., 0., 42., 0., 0.],
                              [44., 0., 0., 0., 0., 0.]],
                             dtype=np.float32))

        np.testing.assert_array_almost_equal(
            out[2], np.array([[30., 0., 0., 0., 0., 0., 0., 0.],
                              [0., 0., 0., 0., 0., 0., 0., 0.],
                              [0., 0., 0., 0., 0., 0., 0., 0.],
                              [0., 0., 0., 0., 0., 0., 0., 0.],
                              [0., 0., 0., 0., 0., 38., 0., 0.],
                              [0., 0., 0., 0., 0., 0., 0., 0.],
                              [0., 0., 0., 0., 0., 0., 0., 0.],
                              [44., 0., 0., 0., 0., 0., 0., 0.]],
                             dtype=np.float32))

        np.testing.assert_array_almost_equal(
            out[3], np.array([[0., 0.],
                              [32., 0.],
                              [0., 0.],
                              [0., 0.],
                              [0., 0.],
                              [40., 0.],
                              [0., 42.],
                              [0., 0.]],
                             dtype=np.float32))

        np.testing.assert_array_almost_equal(
            out[4], np.array([[0., 0., 0., 0., 0., 0., 0., 0.],
                              [0., 0., 0., 0., 0., 0., 0., 0.],
                              [0., 0., 0., 0., 0., 0., 0., 0.],
                              [0., 0., 0., 36., 0., 0., 0., 0.],
                              [0., 0., 0., 0., 0., 0., 0., 0.],
                              [0., 0., 0., 0., 0., 0., 0., 0.],
                              [0., 0., 0., 0., 0., 0., 0., 0.],
                              [0., 0., 0., 0., 0., 0., 0., 0.]],
                             dtype=np.float32))

        np.testing.assert_array_almost_equal(
            out[5], np.array([[0.],
                              [0.],
                              [34.],
                              [0.],
                              [0.],
                              [0.],
                              [0.],
                              [0.]],
                             dtype=np.float32))


if __name__ == '__main__':
    unittest.main()
