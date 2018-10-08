#!/usr/bin/env python3
"""
    Unit tests for analyze_focus.py and select_devs.py.

    Usage:
        Run the script from tools directory.
        python3 -m unittest tests/test_focus.py

"""
import unittest
import os
from helper import load_data, get_log
from analyze_focus import load_selected, get_entropy, get_obj_entropy, extract_extentions,\
    get_counts_obj, extensions_entropy, get_unique_extensions, get_ranges, get_weeks, weekly_entropy, \
    weekly_entropy_sum_days, analyze_weekly, average_ext_number, extension_distribution, get_ext_ranges, \
    get_years_data, get_popular, get_extremes_avg
from select_devs import select, ranges

class TestUnits(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        d = os.path.join('data', 'entropy_groups.json')
        self.groups = load_data(d)
        self.selected = load_selected()
        self.limit = 0
        self.selected_full = load_data('data/test/selected_test.json')
        self.data_list = ['.java', '.java', '.jsp', '.php', '.jsp', '.java']
        self.data_obj = {'.java': 3, '.jsp': 2, '.php': 1}
        self.expected = 1.459147917
        self.years = {'good' : load_data('data/test/test_years_good.json'), 'bad' : load_data('data/test/test_years_bad.json')}
        self.days = {'good': load_data('data/days_good.json'), 'bad': load_data('data/days_bad.json')}
        self.overall = {'good' : load_data('data/test/test_overall_good.json'), 'bad' : load_data('data/test/test_overall_bad.json')}
        self.ranges = load_data('data/entropy_ranges.json')
        self.ranges_vis = load_data('data/entropy_ranges_vis.json')
        dev1 = [ # 3 unique
            ['2017/12/01', ['.java', '.java', '.jsp', '.php', '.jsp', '.java']], # de = 1.459147917
            ['2017/12/02', ['.jsp', '.php', '.jsp', '.java']], # de = 1.5
            ['2017/12/04', ['.jsp', '.php', '.php', '.java']], # de = 1.5
            ['2017/12/23', ['.java']]  # de = 0
        ]
        dev2 = [ # 4 unique
            ["2017/12/06", [".md", ".py" ]], # de = 1
            ["2017/12/15", [".yaml", ".yml", ".yaml", ".yaml", ".yaml", ".yaml", ".py"]], # de = 1.14883
            ["2017/12/16", [".md", ".py", ".yaml", ".yaml"]], # de = 1.5
            ["2017/12/17", [".yaml", ".yaml", ".yaml"]] # de = 0
        ]
        self.ds = {'dev1' : dev1, 'dev2': dev2}
        self.ds_extended = {'dev1' : dev1, 'dev2': dev2, 'dev3': [ ["2017/12/06", [".java", ".py" ]]], 'dev4': [ ["2017/12/06", [".java", ".rb" ]]]}
        self.daily = [
            {
                'name' : 'dev1',
                'data' : [
                    ['2017/12/01', 1.459147917],  # de = 1.459147917
                    ['2017/12/02', 1.5],  # de = 1.5
                    ['2017/12/04', 1.5],  # de = 1.5
                    ['2017/12/23', 0]  # de = 0
                ]
            },
            {
                'name': 'dev2',
                'data': [
                    ["2017/12/06", 1],  # de = 1
                    ["2017/12/15", 1.14883],  # de = 1.14883
                    ["2017/12/16", 1.5],  # de = 1.5
                    ["2017/12/17", 0]  # de = 0
                ]
            }
        ]
        self.devs_ranges = [
            ['dev1', 1],
            ['dev2', 0],
            ['dev3', 0.01],
            ['dev4', 0.001],
            ['dev5', 2],
            ['dev6', 0.1],
            ['dev7', 4]
        ]
        self.devs_ratios = [
            {'dev' : 'dev1', 'commits': {'ratio': 0}},
            {'dev': 'dev2', 'commits': {'ratio': 0.0001}},
            {'dev': 'dev3', 'commits': {'ratio': 0.1}},
            {'dev': 'dev4', 'commits': {'ratio': 0}},
            {'dev': 'dev5', 'commits': {'ratio': 0.2}},
            {'dev': 'dev6', 'commits': {'ratio': 0.01}}
        ]

    def test_groups_bad(self):
        self.assertEqual(len(self.selected['bad']), len(self.groups['bad']), 'grouped bad devs number should be the same')

    def test_groups_good(self):
        self.assertEqual(len(self.selected['good']), len(self.groups['good']), 'grouped good devs number should be the same')

    def test_entropy_list(self):
        actual = get_entropy(self.data_list)
        self.assertEqual(self.expected, round(actual, 9), 'test_entropy_list')

    def test_entropy_obj(self):
        actual = get_obj_entropy(self.data_obj, 6)
        self.assertEqual(self.expected, round(actual, 9), 'test_entropy_obj')

    def test_entropy_methods(self):
        e_obj = get_obj_entropy(self.data_obj, 6)
        e_list = get_entropy(self.data_list)
        self.assertEqual(e_list, e_obj, 'test_entropy_methods')

    def test_daily_sum_good(self):
        """Tests number of extensions -- for all days versus the overall 4 years"""
        daily = 0
        for dev, data in self.days['good'].items():
            for day in data:
                daily += len(day[1])
        overall_sum = len(self.overall['good'])
        self.assertEqual(daily, overall_sum, 'test_daily_sum_good')

    def test_yearly_sum_good(self):
        yearly = 0
        for dev, data in self.years['good'].items():
            for y, extensions in data.items():
                yearly += len(extensions)
        overall_sum = len(self.overall['good'])
        self.assertEqual(yearly, overall_sum, 'test_yearly_sum_good')

    def test_yearly_sum_bad(self):
        yearly = 0
        for dev, data in self.years['bad'].items():
            for y, extensions in data.items():
                yearly += len(extensions)
        overall_sum = len(self.overall['bad'])
        self.assertEqual(yearly, overall_sum, 'test_yearly_sum_bad')

    def test_get_extensions(self):
        files = ['fizz/buzz/some_file.json', '.readme', 'darth/vader/luke.rb', 'this/is/not/a/file']
        expected = ['.json', '.rb']
        actual = extract_extentions(files)
        self.assertEqual(actual, expected, 'test_get_extensions')

    def test_count_obj(self):
        obj = {'2017' : self.data_list}
        ao, al = get_counts_obj(obj)
        eo = {'2017' : self.data_obj}
        el = {'2017' : 6}
        self.assertEqual((ao, al), (eo, el), 'test_count_obj')

    def test_selected_ratios_good(self):
        errors = list()
        for dev in self.selected_full['good']:
            if dev['commits']['ratio'] > self.limit:
                errors.append(dev['dev'])
        self.assertEqual(len(errors), 0, 'test_selected_ratios_good')

    def test_selected_ratios_bad(self):
        errors = list()
        for dev in self.selected_full['bad']:
            if dev['commits']['ratio'] <= self.limit:
                errors.append(dev['dev'])
        self.assertEqual(len(errors), 0, 'test_selected_ratios_bad')

    def test_select(self):
        good, bad = select(self.limit, self.devs_ratios)
        self.assertEqual(len(good), 2, 'number of good devs test_select')
        self.assertEqual(len(bad), 4, 'number of baddevs test_select')
        good_devs = [x['dev'] for x in good]
        self.assertEqual(good_devs, ['dev1', 'dev4'], 'proper good devs test_select')

    def test_ranges(self):
        rs = ranges(self.devs_ratios)
        sum = 0
        for r in rs:
            sum += r[1]
        self.assertEqual(sum, 6, 'test_ranges')

    def test_unique_extensions_num_dev1(self):
        unique = get_unique_extensions(self.ds.get('dev1'))
        self.assertEqual(3, len(unique), 'test_unique_extensions_num_dev1')

    def test_unique_extensions_num_dev2(self):
        unique = get_unique_extensions(self.ds.get('dev2'))
        self.assertEqual(4, len(unique), 'test_unique_extensions_num_dev2')

    def test_unique_extensions_count_dev1_java(self):
        unique = get_unique_extensions(self.ds.get('dev1'))
        self.assertEqual(len(unique.get('.java')), 4, 'test_unique_extensions_count_dev1_java')

    def test_unique_extensions_count_dev1_jsp(self):
        unique = get_unique_extensions(self.ds.get('dev1'))
        self.assertEqual(len(unique.get('.jsp')), 3, 'test_unique_extensions_count_dev1_jsp')

    def test_unique_extensions_count_dev1_php(self):
        unique = get_unique_extensions(self.ds.get('dev1'))
        self.assertEqual(len(unique.get('.php')), 3, 'test_unique_extensions_count_dev1_php')

    def test_extensions_entropy_java(self):
        actual = extensions_entropy(self.ds)
        java_e = -(1/2)*get_log(1/2) - (1/4)*get_log(1/4) - (1/4)*get_log(1/4) - (1)*get_log(1)
        self.assertEqual(java_e, actual.get('dev1').get('.java'), 'test_extensions_entropy_java')

    def test_extensions_entropy_php(self):
        actual = extensions_entropy(self.ds)
        php_e = -(1/6)*get_log(1/6) - (1/4)*get_log(1/4) - (1/2)*get_log(1/2)
        self.assertEqual(php_e, actual.get('dev1').get('.php'), 'test_extensions_entropy_php')

    def test_extensions_entropy_py(self):
        actual = extensions_entropy(self.ds)
        py_e = -(1/2)*get_log(1/2) - (1/7)*get_log(1/7) - (1/4)*get_log(1/4)
        self.assertEqual(py_e, actual.get('dev2').get('.py'), 'test_extensions_entropy_py')

    def test_extensions_entropy_jsp(self):
        actual = extensions_entropy(self.ds)
        jsp_e = -(2 / 6) * get_log(2 / 6) - (2 / 4) * get_log(2 / 4) - (1 / 4) * get_log(1 / 4)
        self.assertEqual(jsp_e, actual.get('dev1').get('.jsp'), 'test_extensions_entropy_jsp')

    def test_average_ext_number(self):
        ext = extensions_entropy(self.ds)
        data = {
            'good' : ext
        }
        actual = average_ext_number(data)
        self.assertEqual(actual['good'], 3.5, 'test_average_ext_number')

    def test_extension_distribution(self):
        ext = extensions_entropy(self.ds)
        java_e = -(1 / 2) * get_log(1 / 2) - (1 / 4) * get_log(1 / 4) - (1 / 4) * get_log(1 / 4) - (1) * get_log(1)
        data = {
            'good': ext
        }
        actual = extension_distribution(data)
        self.assertEqual(actual['good'][1], ['dev1 .java', java_e], 'test_extension_distribution')

    def test_extension_distribution_count(self):
        ext = extensions_entropy(self.ds)
        data = {
            'good': ext
        }
        actual = extension_distribution(data)
        self.assertEqual(len(actual['good']), 7, 'test_extension_distribution_count')

    def test_ext_ranges(self):
        ext = extensions_entropy(self.ds)
        data = {
            'good': ext
        }
        actual = get_ext_ranges(data)
        self.assertEqual(actual['good'].get(0), 0, 'test_ext_ranges limit: 0')
        self.assertEqual(actual['good'].get(1), 3, 'test_ext_ranges limit: 1')
        self.assertEqual(actual['good'].get(2), 4, 'test_ext_ranges limit: 2')
        self.assertEqual(actual['good'].get(5), 0, 'test_ext_ranges limit: 5')

    def test_entropy_ranges(self):
        ranges, rs, cs, fl = get_ranges(self.devs_ranges)
        self.assertEqual(ranges.get(0.001), 2, 'test_entropy_ranges 0.001')
        self.assertEqual(ranges.get(0.01), 1, 'test_entropy_ranges 0.01')
        self.assertEqual(ranges.get(0.1), 1, 'test_entropy_ranges 0.1')
        self.assertEqual(ranges.get(1), 1, 'test_entropy_ranges 1')
        self.assertEqual(ranges.get(2), 1, 'test_entropy_ranges 2')
        self.assertEqual(ranges.get(3), 0, 'test_entropy_ranges 3')
        self.assertEqual(ranges.get(4), 1, 'test_entropy_ranges 4')
        self.assertEqual(ranges.get(5), 0, 'test_entropy_ranges 5')

    def test_ranges_focused(self):
        ranges, rs, cs, fl = get_ranges(self.devs_ranges)
        self.assertEqual(fl[0], 4, 'test_ranges_focused')

    def test_ranges_nf(self):
        ranges, rs, cs, fl = get_ranges(self.devs_ranges)
        self.assertEqual(fl[1], 3, 'test_ranges_nf')

    def test_ranges_sum_good(self):
        sum = 0
        for key, value in self.ranges['good'].items():
            sum += value
        self.assertEqual(sum, len(self.selected['good']), 'test_ranges_sum_good')

    def test_ranges_sum_bad(self):
        sum = 0
        for key, value in self.ranges['bad'].items():
            sum += value
        self.assertEqual(sum, len(self.selected['bad']), 'test_ranges_sum_bad')

    def test_ranges_vis_good(self):
        self.assertEqual(self.ranges['good'].get('0.001'), self.ranges_vis['good'][0], 'test_ranges_vis_good')
        self.assertEqual(self.ranges['good'].get('0.01'), self.ranges_vis['good'][1], 'test_ranges_vis_good')
        self.assertEqual(self.ranges['good'].get('0.1'), self.ranges_vis['good'][2], 'test_ranges_vis_good')
        self.assertEqual(self.ranges['good'].get('1'), self.ranges_vis['good'][3], 'test_ranges_vis_good')
        self.assertEqual(self.ranges['good'].get('2'), self.ranges_vis['good'][4], 'test_ranges_vis_good')
        self.assertEqual(self.ranges['good'].get('3'), self.ranges_vis['good'][5], 'test_ranges_vis_good')
        self.assertEqual(self.ranges['good'].get('4'), self.ranges_vis['good'][6], 'test_ranges_vis_good')
        self.assertEqual(self.ranges['good'].get('5'), self.ranges_vis['good'][7], 'test_ranges_vis_good')

    def test_ranges_vis_bad(self):
        self.assertEqual(self.ranges['bad'].get('0.001'), self.ranges_vis['bad'][0], 'test_ranges_vis_bad')
        self.assertEqual(self.ranges['bad'].get('0.01'), self.ranges_vis['bad'][1], 'test_ranges_vis_bad')
        self.assertEqual(self.ranges['bad'].get('0.1'), self.ranges_vis['bad'][2], 'test_ranges_vis_bad')
        self.assertEqual(self.ranges['bad'].get('1'), self.ranges_vis['bad'][3], 'test_ranges_vis_bad')
        self.assertEqual(self.ranges['bad'].get('2'), self.ranges_vis['bad'][4], 'test_ranges_vis_bad')
        self.assertEqual(self.ranges['bad'].get('3'), self.ranges_vis['bad'][5], 'test_ranges_vis_bad')
        self.assertEqual(self.ranges['bad'].get('4'), self.ranges_vis['bad'][6], 'test_ranges_vis_bad')
        self.assertEqual(self.ranges['bad'].get('5'), self.ranges_vis['bad'][7], 'test_ranges_vis_bad')

    def test_days_empty_good(self):
        errors = list()
        for dev, ds in self.days['good'].items():
            for day in ds:
                if len(day[1]) == 0:
                    errors.append(day)
        self.assertEqual(len(errors), 0, 'test_days_empty_good')

    def test_get_weeks_singles(self):
        """With the sample data each developer should have one year, one week only"""
        actual = get_weeks(self.ds)
        for dev, ys in actual.items():
            for y, weeks in ys.items():
                if weeks is not None:
                    self.assertEqual(len(weeks), 1, 'test_get_weeks_singles')

    def test_get_weeks_exts_number_dev1(self):
        """with the sample data the dev1 should have 10 extensions in it's one week."""
        actual = get_weeks(self.ds)
        for week, exts in actual.get('dev1').get(2017).items():
            self.assertEqual(len(exts), 10, 'test_get_weeks_exts_number_dev1')

    def test_get_weeks_exts_number_dev2(self):
        """with the sample data the dev2 should have 14 extensions in it's one week."""
        actual = get_weeks(self.ds)
        for week, exts in actual.get('dev2').get(2017).items():
            self.assertEqual(len(exts), 14, 'test_get_weeks_exts_number_dev2')

    def test_weekly_entropy_dev1(self):
        data = {'good' : get_weeks(self.ds), 'bad' : get_weeks(self.ds)}
        actual = weekly_entropy(data)
        for week, entropy in actual['good'].get('dev1').get(2017).items():
            self.assertEqual(round(entropy, 12), 1.521928094887, 'test_weekly_entropy_dev1')

    def test_weekly_entropy_dev2(self):
        data = {'good' : get_weeks(self.ds), 'bad' : get_weeks(self.ds)}
        actual = weekly_entropy(data)
        for week, entropy in actual['good'].get('dev2').get(2017).items():
            self.assertEqual(round(entropy, 12), 1.291691997138, 'test_weekly_entropy_dev2')

    def test_weekly_entropy_sum_days_dev1(self):
        data = {'good': self.daily, 'bad': self.daily}
        actual = weekly_entropy_sum_days(data)
        self.assertEqual(round(actual['good'].get('dev1').get(2017).get(48), 9), 2.959147917, 'test_weekly_entropy_sum_days_dev1')

    def test_weekly_entropy_sum_days_dev2(self):
        data = {'good': self.daily, 'bad': self.daily}
        actual = weekly_entropy_sum_days(data)
        self.assertEqual(round(actual['good'].get('dev2').get(2017).get(50), 5), 2.64883, 'test_weekly_entropy_sum_days_dev2')

    def test_analyze_weekly_devs_results_dev1(self):
        data = {'good': get_weeks(self.ds), 'bad': get_weeks(self.ds)}
        weekly = weekly_entropy(data)
        daily = {'good': self.daily, 'bad': self.daily}
        daily_sums = weekly_entropy_sum_days(daily)
        devs_weekly, diffs = analyze_weekly(weekly, daily_sums)
        self.assertEqual(devs_weekly['good'].get('dev1').get('different'), 1, 'test_analyze_weekly_devs_results_dev1 different')
        self.assertEqual(devs_weekly['good'].get('dev1').get('same'), 0, 'test_analyze_weekly_devs_results_dev1 same')
        self.assertEqual(devs_weekly['good'].get('dev1').get('similar'), 0, 'test_analyze_weekly_devs_results_dev1 similar')

    def test_analyze_weekly_summary(self):
        data = {'good': get_weeks(self.ds), 'bad': get_weeks(self.ds)}
        weekly = weekly_entropy(data)
        daily = {'good': self.daily, 'bad': self.daily}
        daily_sums = weekly_entropy_sum_days(daily)
        devs_weekly, diffs = analyze_weekly(weekly, daily_sums)
        self.assertEqual(diffs['good'], [0, 0, 2], 'test_analyze_weekly_summary')

    def test_count_years_dev1(self):
        years = get_years_data(self.ds)
        self.assertEqual(len(years.get('dev1')), 1, 'test_count_years_dev1')

    def test_count_years_dev2(self):
        years = get_years_data(self.ds)
        self.assertEqual(len(years.get('dev2')), 1, 'test_count_years_dev2')

    def test_get_popular(self):
        ext = extensions_entropy(self.ds_extended)
        data = {
            'good': ext
        }
        two = get_popular(data, 2)
        one = get_popular(data, 1)
        self.assertTrue('.java' in one[0], 'test_get_popular for one popular extension')
        self.assertEqual(len(two), 2, 'test_get_popular for four popular extensions')
        self.assertTrue('.java' in two[0], 'test_get_popular for four popular extensions: .java')
        self.assertTrue('.py' in two[1], 'test_get_popular for four popular extensions: .py')

    def test_get_extremes_avg(self):
        ext = extensions_entropy(self.ds_extended)
        data = {
            'good': ext,
            'bad': ext
        }
        extremes, avgs = get_extremes_avg(data)
        jsp_e = -(2 / 6) * get_log(2 / 6) - (2 / 4) * get_log(2 / 4) - (1 / 4) * get_log(1 / 4)
        self.assertEqual(len(extremes['good']), 0, 'test_get_extremes_avg list of min should be empty')
        self.assertEqual(avgs['good']['.jsp'][1], set(['dev1']), 'test_get_extremes_avg avg developers .jsp')
        self.assertEqual(avgs['good']['.java'][1], set(['dev1', 'dev3', 'dev4']), 'test_get_extremes_avg avg developers .jsp')
        self.assertEqual(avgs['good']['.jsp'][0], jsp_e, 'test_get_extremes_avg avg entropy sum .jsp')
        self.assertEqual(avgs['good']['.jsp'][2], jsp_e, 'test_get_extremes_avg avg entropy avg .jsp')


if __name__ == '__main__':
    unittest.main()