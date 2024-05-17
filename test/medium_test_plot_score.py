try:
    import matplotlib  # noqa: F401
    import pandas  # noqa: F401
except ImportError:
    pandas = None
import os
import IMP.test
from IMP.sampcon import plot_score


class Tests(IMP.test.TestCase):
    def test_plot_score_help(self):
        """Test plot_score module help"""
        self.check_runnable_python_module("IMP.sampcon.plot_score")

    def test_plot_score_one(self):
        """Test plot_score.py with one score"""
        if pandas is None:
            self.skipTest(
                "this test requires the matplotlib and pandas Python modules")
        self.run_python_module(
            plot_score,
            [self.get_input_file_name('model_ids_scores.txt'),
             'CrossLinkingMassSpectrometryRestraint_Data_Score_Chen'])
        os.unlink('CrossLinkingMassSpectrometryRestraint_Data_Score_Chen.png')

    def test_plot_score_all(self):
        """Test plot_score.py with all scores"""
        if pandas is None:
            self.skipTest(
                "this test requires the matplotlib and pandas Python modules")
        expected = [
            'ConnectivityRestraint_Rpb1.png',
            'CrossLinkingMassSpectrometryRestraint_Distance_.png',
            'CrossLinkingMassSpectrometryRestraint_Data_Score_Chen.png',
            'Total_Score.png',
            'ExcludedVolumeSphere_None.png']
        self.run_python_module(
            plot_score,
            [self.get_input_file_name('model_ids_scores.txt'), 'all'])
        for e in expected:
            os.unlink(e)

    def test_plot_score_bad(self):
        """Test plot_score.py with bad score"""
        if pandas is None:
            self.skipTest(
                "this test requires the matplotlib and pandas Python modules")
        self.assertRaises(
            KeyError, self.run_python_module, plot_score,
            [self.get_input_file_name('model_ids_scores.txt'), 'garbage'])


if __name__ == '__main__':
    IMP.test.main()
