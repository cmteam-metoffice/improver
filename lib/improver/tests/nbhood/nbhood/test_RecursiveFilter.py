# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
"""Unit tests for the nbhood.RecursiveFilter plugin."""

import unittest
from iris.cube import Cube
from iris.tests import IrisTest
from iris.coords import DimCoord
from cf_units import Unit
import numpy as np
from improver.nbhood.recursive_filter import RecursiveFilter
from improver.nbhood.square_kernel import SquareNeighbourhood


class Test__repr__(IrisTest):

    """Test the repr method."""

    def test_basic(self):
        """Test that the __repr__ returns the expected string."""
        alpha_x = None
        alpha_y = None
        iterations = None
        edge_width = 1
        result = str(RecursiveFilter(alpha_x, alpha_y, iterations, edge_width))
        msg = ('<RecursiveFilter: alpha_x: {}, alpha_y: {}, iterations: {},'
               ' edge_width: {}'.format(alpha_x, alpha_y,
                                        iterations, edge_width))
        self.assertEqual(result, msg)


class Test_RecursiveFilter(IrisTest):

    """Test class for the RecursiveFilter tests, setting up cubes."""

    def setUp(self):
        """Create test cubes."""

        self.alpha_x = 0.5
        self.alpha_y = 0.5
        self.iterations = 1

        # Generate data cube with dimensions 5 x 5
        data = np.zeros((1, 5, 5))
        data[0][0][2] = 0.1
        data[0][1][2] = 0.25
        data[0][2][2] = 0.5
        data[0][3][2] = 0.25
        data[0][4][2] = 0.1
        data[0][2][0] = 0.1
        data[0][2][1] = 0.25
        data[0][2][3] = 0.25
        data[0][2][4] = 0.1

        cube = Cube(data, standard_name="precipitation_amount",
                    units="kg m^-2 s^-1")
        cube.add_dim_coord(DimCoord(np.linspace(-45.0, 45.0, 5), 'latitude',
                                    units='degrees'), 1)
        cube.add_dim_coord(DimCoord(np.linspace(120, 180, 5), 'longitude',
                                    units='degrees'), 2)
        time_origin = "hours since 1970-01-01 00:00:00"
        calendar = "gregorian"
        tunit = Unit(time_origin, calendar)
        cube.add_dim_coord(DimCoord([402192.5],
                                    "time", units=tunit), 0)
        self.cube = cube

        # Generate alphas_cube with dimensions 5 x 5
        alphas_data1 = np.ones((5, 5)) * 0.5
        alphas_cube1 = Cube(alphas_data1)
        alphas_cube1.add_dim_coord(DimCoord(np.linspace(-45.0, 45.0, 5),
                                            'latitude', units='degrees'), 0)
        alphas_cube1.add_dim_coord(DimCoord(np.linspace(120, 180, 5),
                                            'longitude', units='degrees'), 1)
        self.alphas_cube1 = alphas_cube1

        # Generate alphas_cube with dimensions 6 x 6
        alphas_data2 = np.ones((6, 6)) * 0.5
        alphas_cube2 = Cube(alphas_data2)
        alphas_cube2.add_dim_coord(DimCoord(np.linspace(-45.0, 45.0, 6),
                                            'latitude', units='degrees'), 0)
        alphas_cube2.add_dim_coord(DimCoord(np.linspace(120, 180, 6),
                                            'longitude', units='degrees'), 1)
        self.alphas_cube2 = alphas_cube2


class Test__init__(Test_RecursiveFilter):

    """Test plugin initialisation."""

    def test_alpha_x_gt_unity(self):
        """Test when an alpha_x value > unity is given (invalid)."""
        alpha_x = 1.1
        msg = "Invalid alpha_x: must be > 0 and < 1: 1.1"
        with self.assertRaisesRegexp(ValueError, msg):
            RecursiveFilter(alpha_x=alpha_x, alpha_y=None,
                            iterations=None, edge_width=1)

    def test_alpha_x_lt_zero(self):
        """Test when an alpha_x value <= zero is given (invalid)."""
        alpha_x = -0.5
        msg = "Invalid alpha_x: must be > 0 and < 1: -0.5"
        with self.assertRaisesRegexp(ValueError, msg):
            RecursiveFilter(alpha_x=alpha_x, alpha_y=None,
                            iterations=None, edge_width=1)

    def test_alpha_y_gt_unity(self):
        """Test when an alpha_y value > unity is given (invalid)."""
        alpha_y = 1.1
        msg = "Invalid alpha_y: must be > 0 and < 1: 1.1"
        with self.assertRaisesRegexp(ValueError, msg):
            RecursiveFilter(alpha_x=None, alpha_y=alpha_y,
                            iterations=None, edge_width=1)

    def test_alpha_y_lt_zero(self):
        """Test when an alpha_y value <= zero is given (invalid)."""
        alpha_y = -0.5
        msg = "Invalid alpha_y: must be > 0 and < 1: -0.5"
        with self.assertRaisesRegexp(ValueError, msg):
            RecursiveFilter(alpha_x=None, alpha_y=alpha_y,
                            iterations=None, edge_width=1)

    def test_iterations(self):
        """Test when iterations value less than unity is given (invalid)."""
        iterations = 0
        msg = "Invalid number of iterations: must be >= 1: 0"
        with self.assertRaisesRegexp(ValueError, msg):
            RecursiveFilter(alpha_x=None, alpha_y=None,
                            iterations=iterations, edge_width=1)


class Test_set_alphas(Test_RecursiveFilter):

    """Test the set_alphas function"""

    def test_alpha_x_used_result(self):
        """Test that the returned alphas array has the expected result
           when alphas_cube=None."""
        result = RecursiveFilter().set_alphas(self.cube, self.alpha_x, None)
        expected_result = 0.5
        self.assertIsInstance(result.data, np.ndarray)
        self.assertEqual(result.data[0][2], expected_result)
        # Check shape: Array should be padded with 4 extra rows/columns
        expected_shape = (9, 9)
        self.assertEqual(result.shape, expected_shape)

    def test_alphas_cube_used_result(self):
        """Test that the returned alphas array has the expected result
           when alphas_cube is not None."""
        result = RecursiveFilter().set_alphas(self.cube[0, :], None,
                                              self.alphas_cube1)
        expected_result = 0.5
        self.assertIsInstance(result.data, np.ndarray)
        self.assertEqual(result.data[0][2], expected_result)
        # Check shape: Array should be padded with 4 extra rows/columns
        expected_shape = (9, 9)
        self.assertEqual(result.shape, expected_shape)

    def test_mismatched_dimensions_alphas_cube_data_cube(self):
        """Test that an error is raised if the alphas_cube is of a different
        shape to the data cube."""
        msg = "Dimensions of alphas array do not match dimensions "
        with self.assertRaisesRegexp(ValueError, msg):
            RecursiveFilter().set_alphas(self.cube, None, self.alphas_cube2)

    def test_alphas_cube_and_alpha_not_set(self):
        """Test error is raised when both alphas_cube and alpha are set
           to None (invalid)."""
        alpha = None
        alphas_cube = None
        msg = "A value for alpha must be set if alphas_cube is "
        with self.assertRaisesRegexp(ValueError, msg):
            RecursiveFilter().set_alphas(self.cube, alpha, alphas_cube)

    def test_alphas_cube_and_alpha_both_set(self):
        """Test error is raised when both alphas_cube and alpha are set."""
        alpha = 0.5
        alphas_cube = self.alphas_cube1
        msg = "A cube of alpha values and a single float value for"
        with self.assertRaisesRegexp(ValueError, msg):
            RecursiveFilter().set_alphas(self.cube, alpha, alphas_cube)


class Test_recurse_forward_x(Test_RecursiveFilter):

    """Test the recurse_forward_x method"""

    def test_basic_method(self):
        """Test that the returned recurse_forward_x array has the expected
           type and result."""
        result = RecursiveFilter().recurse_forward_x(
            self.cube.data[0, :], self.alphas_cube1.data)
        expected_result = 0.196875
        self.assertIsInstance(result, np.ndarray)
        self.assertAlmostEqual(result[4][2], expected_result)


class Test_recurse_backwards_x(Test_RecursiveFilter):

    """Test the recurse_backwards_x method"""

    def test_basic_method(self):
        """Test that the returned recurse_backwards_x array has the expected
           type and result."""
        result = RecursiveFilter().recurse_backwards_x(
            self.cube.data[0, :], self.alphas_cube1.data)
        expected_result = 0.196875
        self.assertIsInstance(result, np.ndarray)
        self.assertAlmostEqual(result[0][2], expected_result)


class Test_recurse_forward_y(Test_RecursiveFilter):

    """Test the recurse_forward_y method"""

    def test_basic_method(self):
        """Test that the returned recurse_forward_y array has the expected
           type and result."""
        result = RecursiveFilter().recurse_forward_y(
            self.cube.data[0, :], self.alphas_cube1.data)
        expected_result = 0.0125
        self.assertIsInstance(result, np.ndarray)
        self.assertAlmostEqual(result[0][4], expected_result)


class Test_recurse_backwards_y(Test_RecursiveFilter):

    """Test the recurse_backwards_y method"""

    def test_basic_method(self):
        """Test that the returned recurse_backwards_y array has the expected
           type and result."""
        result = RecursiveFilter().recurse_backwards_y(
            self.cube.data[0, :], self.alphas_cube1.data)
        expected_result = 0.0125
        self.assertIsInstance(result, np.ndarray)
        self.assertAlmostEqual(result[0][0], expected_result)


class Test_run_recursion(Test_RecursiveFilter):

    """Test the run_recursion method"""

    def test_return_type(self):
        """Test that the run_recursion method returns an iris.cube.Cube."""
        edge_width = 1
        alphas_x = RecursiveFilter().set_alphas(self.cube, self.alpha_x, None)
        alphas_y = RecursiveFilter().set_alphas(self.cube, self.alpha_y, None)
        padded_cube = SquareNeighbourhood().pad_cube_with_halo(
            self.cube, edge_width, edge_width)
        result = RecursiveFilter().run_recursion(
            padded_cube, alphas_x, alphas_y, self.iterations)
        self.assertIsInstance(result, Cube)

    def test_expected_result(self):
        """Test that the run_recursion method returns the expected value."""
        edge_width = 1
        alphas_x = RecursiveFilter().set_alphas(self.cube, self.alpha_x, None)
        alphas_y = RecursiveFilter().set_alphas(self.cube, self.alpha_y, None)
        padded_cube = SquareNeighbourhood().pad_cube_with_halo(
            self.cube, edge_width, edge_width)
        result = RecursiveFilter().run_recursion(
            padded_cube, alphas_x, alphas_y, self.iterations)
        expected_result = 0.13382206
        self.assertAlmostEqual(result.data[4][4], expected_result)


class Test_process(Test_RecursiveFilter):

    """Test the process method. """

    # Test output from plugin returns expected values
    def test_return_type(self):
        """Test that the RecursiveFilter plugin returns an iris.cube.Cube."""
        plugin = RecursiveFilter(alpha_x=self.alpha_x, alpha_y=self.alpha_y,
                                 iterations=self.iterations)
        result = plugin.process(self.cube, alphas_x=None, alphas_y=None)
        self.assertIsInstance(result, Cube)

    def test_alpha_floats(self):
        """Test that the RecursiveFilter plugin returns the correct data
        when using float alpha values."""
        plugin = RecursiveFilter(alpha_x=self.alpha_x, alpha_y=self.alpha_y,
                                 iterations=self.iterations)
        result = plugin.process(self.cube, alphas_x=None, alphas_y=None)
        expected = 0.13382206
        self.assertAlmostEqual(result.data[0][2][2], expected)

    def test_alpha_cubes(self):
        """Test that the RecursiveFilter plugin returns the correct data
        when using alpha cubes."""
        plugin = RecursiveFilter(alpha_x=None, alpha_y=None,
                                 iterations=self.iterations)
        result = plugin.process(self.cube, alphas_x=self.alphas_cube1,
                                alphas_y=self.alphas_cube1)
        expected = 0.13382206
        self.assertAlmostEqual(result.data[0][2][2], expected)

    def test_alpha_floats_nan_in_data(self):
        """Test that the RecursiveFilter plugin returns the correct data
        when using float alpha values and the data contains nans."""
        plugin = RecursiveFilter(alpha_x=self.alpha_x, alpha_y=self.alpha_y,
                                 iterations=self.iterations)
        self.cube.data[0][3][2] = np.nan
        result = plugin.process(self.cube, alphas_x=None, alphas_y=None)
        expected = 0.11979733
        self.assertAlmostEqual(result.data[0][2][2], expected)

    def test_alpha_floats_nan_in_masked_data(self):
        """Test that the RecursiveFilter plugin returns the correct data
        when using float alpha values, the data contains nans and the data
        is masked (but not the nan value)."""
        plugin = RecursiveFilter(alpha_x=self.alpha_x, alpha_y=self.alpha_y,
                                 iterations=self.iterations)
        self.cube.data[0][3][2] = np.nan
        mask = np.zeros((self.cube.data.shape))
        mask[0][1][2] = 1
        self.cube.data = np.ma.MaskedArray(self.cube.data, mask=mask)
        result = plugin.process(self.cube, alphas_x=None, alphas_y=None)
        expected = 0.105854129
        self.assertAlmostEqual(result.data[0][2][2], expected)

    def test_alpha_cubes_masked_data(self):
        """Test that the RecursiveFilter plugin returns the correct data
        when using alpha cubes and a masked data cube."""
        plugin = RecursiveFilter(alpha_x=None, alpha_y=None,
                                 iterations=self.iterations)
        mask = np.zeros((self.cube.data.shape))
        mask[0][3][2] = 1
        self.cube.data = np.ma.MaskedArray(self.cube.data, mask=mask)
        result = plugin.process(self.cube, alphas_x=self.alphas_cube1,
                                alphas_y=self.alphas_cube1)
        expected = 0.11979733
        self.assertAlmostEqual(result.data[0][2][2], expected)

    def test_dimensions_of_output_array_is_as_expected(self):
        """Test that the RecursiveFilter plugin returns a data array with
           the correct dimensions"""
        plugin = RecursiveFilter(alpha_x=self.alpha_x, alpha_y=self.alpha_y,
                                 iterations=self.iterations)
        result = plugin.process(self.cube, alphas_x=None, alphas_y=None)
        # Output data array should have same dimensions as input data array
        expected_shape = (1, 5, 5)
        self.assertEqual(result.data.shape, expected_shape)
        self.assertEqual(result.data.shape, expected_shape)


if __name__ == '__main__':
    unittest.main()
