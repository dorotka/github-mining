#!/usr/bin/env python3
"""
    Runs analysis of developers focus based on extensions. The analysis is done for different time periods : day, week, year, 4 years.
    Uses data/selected.json, data/authors_combined as input.

    Usage:
        python3 _analyze_focus.py

"""
import os
from helper import save_in_file, load_data
from logger import log_debug, log_info
from os import path
from time import time
from datetime import datetime
import math


test = False


def load_selected():
    dir = path.join('data', 'selected.json')
    return load_data(dir)


def load_authors():
    dir = path.join('data', 'authors_combined.json')
    return load_data(dir)


def extract_extentions(files):
    """Returns a list of unique extentions from the files."""
    extensions = list()
    for file in files:
        if file is None:
            continue
        n, ext = os.path.splitext(file)
        if ext != '':
            extensions.append(ext)
    return extensions


def set_up_groups():
    """divide per_author into good and bad, either save or keep in memory"""
    rated = load_selected()
    log_debug(None, 'Number of good selected dev is {0[0]} and bad ones is {0[1]}.', (len(rated['good']), len(rated['bad'])))
    groups = {
        'good' : dict(),
        'bad' : dict()
    }
    good = 0
    bad = 0
    authors = load_authors()
    for dev, dates in authors.items():
        if dev in rated['good']:
            good += 1
            groups['good'].update({dev: dates})
        elif dev in rated['bad']:
            bad += 1
            groups['bad'].update({dev: dates})
        else:
            log_debug(None, 'Developer was not classified : {0[0]}', (dev,))
    log_debug(None, 'Number of good devs is {0[0]}, and bad ones is {0[1]}', (len(list(groups['good'].keys())), len(list(groups['bad'].keys()))))
    return groups


def load_ratios():
    """Load ratios for developer and return as a dictionary"""
    dir = os.path.join('data', 'authors_ratio.json')
    ratios_list = load_data(dir)
    ratios = dict()
    for r in ratios_list:
        ratios.update({r['dev'] : r['commits']['ratio']})
    return ratios


def get_entropy(data):
    """Get entropy for data formatted as list"""
    entropy = 0
    seen = list()
    for x in data:
        if x not in seen:
            seen.append(x)
            p_x = float(data.count(x)) / len(data)
            if p_x > 0:
                entropy += - p_x * math.log(p_x, 2)
    return entropy


def get_obj_entropy(data, sum):
    """"Get entropy for data formatted as a dictionary"""
    entropy = 0
    for x, c in data.items():
        p_x = float(c) / sum
        if p_x > 0:
            entropy += - p_x * math.log(p_x, 2)
    return entropy


def get_data(authors, g):
    """Get extensions data per period"""
    days = dict()
    devs = dict()
    test_overall = list()
    for dev, dates in authors.items():
        days[dev] = list()
        for date, info in dates.items():
            exts = list()
            day = [date, exts]
            for c in info['commits']:
                for sha, files in c.items():
                    fs = [x['new'] for x in files]
                    extensions = extract_extentions(fs)
                    exts.extend(extensions)
                    test_overall.extend(extensions)
            if len(day[1]) > 0:
                days[dev].append(day)
            # devs
            if devs.get(dev) is None:
                devs.update({dev: list(day[1])})
            else:
                devs[dev].extend(day[1])
    years = get_years_data(days)
    nd = 'days_' + g + '.json'
    save_in_file(days, nd, 'data')
    if test:
        ny = 'test_years_' + g + '.json'
        to = 'test_overall_' + g + '.json'
        save_in_file(years, ny, 'data/test')
        save_in_file(test_overall, to, 'data/test')
    return {'days': days, 'years': years, 'devs' : devs}


def get_years_data(days):
    """Set up extension data for years"""
    years = dict()
    for dev, data in days.items():
        years[dev] = dict()
        for day in data:
            y = datetime.strptime(day[0], '%Y/%m/%d').year
            if years[dev].get(y) is None:
                years[dev].update({y: list(day[1])})
            else:
                years[dev].get(y).extend(day[1])
    return years


def get_counts_obj(data):
    """Return unique extensions and the counts of occurrences"""
    sums = dict()
    for key, values in data.items():
        sum = len(values)
        ext = dict()
        for e in values:
            if ext.get(e) is None:
                ext.update({e: values.count(e)})
        data[key] = ext
        sums.update({key: sum})
    return (data, sums)


def get_counts_years(data):
    for dev, values in data.items():
        for y, extensions in values.items():
            ext = dict()
            sum = len(extensions)
            for e in extensions:
                if ext.get(e) is None:
                    ext.update({e: extensions.count(e)})
            data[dev][y] = {'extensions' : ext}
            data[dev][y].update({'sum' : sum})
    if test:
        save_in_file(data, 'test_years_count.json', 'data/test')
    return data


def daily_entropy(days, g):
    """Setup daily entropy data to be visualized"""
    if g == 'good':
        color = 'rgba(119, 152, 191, .5)'
    else:
        color = 'rgba(223, 83, 83, .5)'
    de = list()
    for dev, dates in days.items():
        for d in dates:
            e = get_entropy(d[1])
            d[1] = e
        e_sorted = sorted(dates, key=lambda x: datetime.strptime(x[0], '%Y/%m/%d'))
        de.append({'name' : dev, 'color' : color, 'data' : e_sorted})
    return de


def yearly_entropy(years, g, py):
    """Setup yearly entropy data to be visualized"""
    if g == 'good':
        color = 'rgba(119, 152, 191, .5)'
    else:
        color = 'rgba(223, 83, 83, .5)'
    ye = list()
    for dev, years_counted in years.items():
        per_year = [0, 0, 0, 0]
        for year, data in years_counted.items():
            en = get_obj_entropy(data.get('extensions'), data.get('sum'))
            per_year[year-2014] = en
            py.get(year).get(g).append([dev, en])
        ye.append({'name': dev, 'color': color, 'data': per_year})
        py.get(year)[g] = sorted(py.get(year).get(g), key=lambda x: x[1], reverse=True)
    return ye


def per_dev_entropy(devs_counted, devs_sums, ratios):
    """Set up [ratio, entropy] to visualize per deveoper. Over 4 years."""
    pde = list()
    just_entropy = list()
    for dev, es in devs_counted.items():
        entr = get_obj_entropy(es, devs_sums.get(dev))
        r = ratios.get(dev)
        pde.append([r, entr])
        just_entropy.append([dev, entr])
    just_entropy = sorted(just_entropy, key=lambda x: x[1], reverse=True)
    return pde, just_entropy


def analyze_extensions(groups, ratios):
    """Save the focus entropy results for time period."""
    entropies = {
        'good' : None,
        'bad' : None
    }
    daily = {
        'good' : list(),
        'bad' : list()
    }
    yearly = {
        'good': list(),
        'bad': list(),
        'all' : list()
    }
    per_year = {
        2014 : {
            'good': list(),
            'bad' : list()
        },
        2015: {
            'good': list(),
            'bad': list()
        },
        2016 : {
            'good': list(),
            'bad' : list()
        },
        2017: {
            'good': list(),
            'bad': list()
        }
    }
    per_dev = {
        'good' : list(),
        'bad' : list()
    }
    ranges_vis = {
        'categories' : list(),
        'good' : list(),
        'bad' : list()
    }
    focus_level = {
        'good' : None,
        'bad' : None
    }
    entr_devs = {
        'good' : None,
        'bad' : None
    }
    for g, authors in groups.items():
        T = time()
        data = get_data(authors, g)
        days = data.get('days')
        years = data.get('years')
        devs = data.get('devs')
        years_counted = get_counts_years(years)
        devs_counted, devs_sums = get_counts_obj(devs)
        log_debug(None, 'Data prepared in {0[0]}', (time()-T,))
        daily[g] = daily_entropy(days, g)
        ye = yearly_entropy(years_counted, g, per_year)
        yearly[g] = ye
        yearly['all'].extend(ye)
        per_dev[g], pd = per_dev_entropy(devs_counted, devs_sums, ratios)
        ranges = get_ranges(per_dev[g])
        entropies[g] = ranges[0]
        ranges_vis['categories'] = ranges[2]
        ranges_vis[g] = ranges[1]
        focus_level[g] = ranges[3]
        log_info(None, 'Ranges for {0[0]} devs: {0[1]}', (g, entropies[g]))
        entr_devs[g] = pd
    log_info(None, 'Focus levels are {0[0]}', (focus_level,))
    save_in_file(daily, 'entropy_daily.json', 'data')
    save_in_file(yearly, 'entropy_yearly.json', 'data')
    save_in_file(per_year, 'entropy_per_year.json', 'data')
    save_in_file(per_dev, 'entropy_per_dev.json', 'data')
    save_in_file(entr_devs, 'entropy_all.json', 'data')
    save_in_file(entropies, 'entropy_ranges.json', 'data')
    save_in_file(ranges_vis, 'entropy_ranges_vis.json', 'data')


def get_weeks(days):
    """Set up the data per week. Remove weeks that contain only one day."""
    weekly = dict()
    one = dict()
    total = 0
    one_count = 0
    single_day = 0
    single_day_dev = set()
    for dev, dates in days.items():
        weeks = {
            2014: None,
            2015: None,
            2016: None,
            2017: None
        }
        weeks1 = {
            2014: None,
            2015: None,
            2016: None,
            2017: None
        }
        weekly.update({dev : weeks})
        one.update({dev: weeks1})
        for day in dates:
            year = datetime.strptime(day[0], '%Y/%m/%d').year
            week = datetime.strptime(day[0], '%Y/%m/%d').isocalendar()[1]
            if weeks.get(year) is None:
                weeks[year] = {week : list(day[1])}
                weeks1[year] = {week : day[0]}
                total += 1
            else:
                if weeks.get(year).get(week) is None:
                    weeks.get(year).update({week : list(day[1])})
                    weeks1.get(year).update({week : day[0]})
                    total += 1
                else:
                    weeks.get(year)[week].extend(list(day[1]))
                    weeks1.get(year)[week] = 0
                    del weeks1[year][week]
                    total += 1
        # remove weeks with one day only
        for y, w in weeks1.items():
            single_day_dev.add(dev)
            if w is None:
                continue
            for wn in w.keys():
                del weeks[y][wn]
                single_day += 1
    log_info(None, 'Number of week with a single active day is {0[0]}, for {0[1]} developers.', (single_day, len(list(single_day_dev))))
    for ys in one.values():
        for ws in ys.values():
            if ws is None:
                continue
            one_count += len(ws)
    log_debug(None, 'Number of weeks with one day in a week is {0[0]} out of {0[1]}.', (one_count, total))
    return weekly


def weekly_entropy(weekly):
    """Get weekly entropy"""
    for g, devs in weekly.items():
        for dev, dates in devs.items():
            for year, weeks in dates.items():
                if weeks is None:
                    continue
                for week, extensions in weeks.items():
                    entropy = get_entropy(extensions)
                    weeks[week] = entropy
    return weekly


def weekly_entropy_sum_days(days):
    """Get a sum of daily entropy values per week."""
    entropy_sums = {
        'good' : dict(),
        'bad' : dict()
    }
    for g, devs in days.items():
        for dev in devs:
            weeks = {
                2014: None,
                2015: None,
                2016: None,
                2017: None
            }
            entropy_sums[g].update({dev['name'] : weeks})
            for day in dev['data']:
                year = datetime.strptime(day[0], '%Y/%m/%d').year
                week = datetime.strptime(day[0], '%Y/%m/%d').isocalendar()[1]
                if weeks.get(year) is None:
                    weeks[year] = {week : day[1]}
                elif weeks.get(year).get(week) is None:
                    weeks.get(year).update({week : day[1]})
                else:
                    weeks.get(year)[week] += day[1]
    return entropy_sums


def analyze_weekly(weekly, daily_sums):
    """The developer is categories based on the larges number fo weeks falling into categories:
    same, similar, different. If majority of weeks for the dev is similar, then the dev is added to similar, if same,
    then added to same otherwise to different."""
    devs_weekly = {'good' : dict(), 'bad' : dict()}
    same_count = 0
    same_zero = 0
    for g, devs in weekly.items():
        for dev, years in devs.items():
            devs_weekly[g].update({dev: {'same' : 0, 'similar' : 0, 'different' : 0}})
            for year, weeks in years.items():
                if weeks is None:
                    continue
                for week, entropy in weeks.items():
                    difference = abs(entropy - daily_sums.get(g).get(dev).get(year).get(week))
                    if difference == 0:
                        devs_weekly[g][dev]['same'] += 1
                        same_count += 1
                        if entropy == 0:
                            same_zero += 1
                    elif difference < 0.1:
                        devs_weekly[g][dev]['similar'] += 1
                    else:
                        devs_weekly[g][dev]['different'] += 1
    diffs = {
        'good' : [0, 0, 0],
        'bad' : [0, 0, 0]
    }
    # number of developers for each category - same, similar, good
    for g, devs in devs_weekly.items():
        for dev, differences in devs.items():
            if differences.get('similar') + differences.get('same') > differences.get('different'):
                if differences.get('similar') > differences.get('same'):
                    diffs[g][1] += 1
                else:
                    diffs[g][0] += 1
            else:
                diffs[g][2] += 1
    log_info(None, 'Diffs [same, similar, different]: {0[0]}', (diffs,))
    return devs_weekly, diffs


def compare_weeks_daily_sums():
    """Compare weekly entropy values with the sums of daily per week. Save the results."""
    days = {'good': load_data('data/days_good.json'), 'bad': load_data('data/days_bad.json')}
    weeks = {'good': get_weeks(days['good']), 'bad': get_weeks(days['bad'])}
    if test:
        save_in_file(weeks, 'test_weekly.json', 'data/test')
    weeks_entropy = weekly_entropy(weeks)
    save_in_file(weeks_entropy, 'entropy_weekly.json', 'data')
    daily_entropies = load_data('data/entropy_daily.json')
    weeks_sums_daily = weekly_entropy_sum_days(daily_entropies)
    # save_in_file(weeks_sums_daily, 'entropy_weeks_sums_daily.json', 'data')
    weeks_analyzed, summary = analyze_weekly(weeks_entropy, weeks_sums_daily)
    save_in_file(weeks_analyzed, 'entropy_weeks_analyzed.json', 'data')


def get_unique_extensions(dates):
    """Get unique extensions."""
    uniques = dict()
    for day in dates:
        # to avoid duplicates, populate seen
        seen = dict()
        for ext in day[1]:
            if seen.get(ext) is None:
                seen.update({ext: list()})
            if uniques.get(ext) is None:
                uniques.update({ext: [list(day)]})
                seen.get(ext).append(list(day))
            else:
                if day not in seen.get(ext):
                    seen.get(ext).append(list(day))
                    uniques.get(ext).append(list(day))
    if test:
        save_in_file(uniques, 'test_uniques.json', 'data/test')
    return uniques


def extensions_entropies():
    """Return extension entropy for good and bad developers."""
    days = {'good': load_data('data/days_good.json'), 'bad': load_data('data/days_bad.json')}
    entropies = {'good' : None, 'bad' : None}
    for g, data in days.items():
        entropy = extensions_entropy(data)
        entropies[g] = entropy
    return entropies


def extensions_entropy(days):
    """Get extension entropy for developers."""
    entropies = dict()
    for dev, dates in days.items():
        entropies[dev] = dict()
        uniques = get_unique_extensions(dates)
        for ext, ds in uniques.items():
            # get entropy for this extension only
            entropy = 0
            for day in ds:
                p_x = float(day[1].count(ext)) / len(day[1])
                if p_x > 0:
                    entropy -= p_x * math.log(p_x, 2)
            entropies.get(dev).update({ext: entropy})
    return entropies


def average_ext_number(ext):
    """Get average number of extensions per developer."""
    avg = {
        'good' : 0,
        'bad' : 0
    }
    for g, data in ext.items():
        sum = 0
        devs = len(data)
        for dev, extensions in data.items():
            sum += len(extensions)
        avg[g] = sum/devs
    log_info(None, 'Average extensions for good devs: {0[0]} and bad devs: {0[1]}.', (avg['good'], avg['bad']))
    return avg


def extension_distribution(ext):
    """Get entropy values for each developer-extension pair."""
    distribution = {
        'good' : list(),
        'bad' : list()
    }
    for g, data in ext.items():
        for dev, extensions in data.items():
            for extension, entropy in extensions.items():
                name = dev + ' ' + extension
                point = [name, entropy]
                distribution[g].append(point)
        distribution[g] = sorted(distribution[g], key=lambda x: x[1], reverse=True)
    return distribution


def get_ext_ranges(ext):
    """Get extensions ranges."""
    rs = {
        'good' : None,
        'bad' : None
    }
    for g, data in ext.items():
        total = 0
        ranges = {0: 0, 1: 0, 2: 0, 5: 0, 10: 0, 20: 0, 50: 0, 100: 0, 200: 0}
        for dev, extensions in data.items():
            for extension, entropy in extensions.items():
                total += 1
                for limit in list(ranges.keys()):
                    if entropy <= limit:
                        ranges[limit] += 1
                        break
        log_info(None, 'Per extension etropy: {0[0]} devs ranges: {0[1]}. Total: {0[2]}.', (g, ranges, total))
        rs[g] = ranges
    return rs


def get_popular(extensions, num):
    """Find the extensions used by most of the developers in the set"""
    ext_count = dict()
    ext_list = list()
    for group, devs in extensions.items():
        for dev, exts in devs.items():
            for ext in exts.keys():
                if ext_count.get(ext) is None:
                    ext_count.update({ext: 1})
                else:
                    ext_count[ext] += 1
    for ext, count in ext_count.items():
        ext_list.append([ext, count])
    sorted_exts = sorted(ext_list, key=lambda x: x[1], reverse=True)
    return sorted_exts[0:num]


def compare_most_popular(extensions):
    """Setup visualization data for the most popular extensions.
    Data contains all developers working on the extension and the corresponsing entropy value."""
    popular = get_popular(extensions, 10)
    data = dict()
    for extension in popular:
        data.update({extension[0]: {'good': {'name': 'Good', 'color': 'rgba(119, 152, 191, .5)', 'data': list() }, 'bad': {'name': 'Bad', 'color': 'rgba(223, 83, 83, .5)', 'data': list() }}})
    for group, devs in extensions.items():
        for dev, exts in devs.items():
            for ext, entropy in exts.items():
                if data.get(ext) is None:
                    continue
                data.get(ext).get(group)['data'].append([dev, entropy])
    for ext, d in data.items():
        for group, series in d.items():
            series['data'] = sorted(series['data'], key=lambda x: x[1], reverse=True)
    return data


def get_extremes_avg(extensions, fpe):
    """
    Get average entropy per extension accross a group of developers. Select min (averages of 0) and 2 max values.
    Compare the extremes (mins and maxs) against the entropy values for the other group.
    :param extensions:
    :param fpe: files per extension
    :return: extremes dict, avgs dict
    """
    extremes = {
        'good': list(), # [min1, min2, ...]
        'bad': list() # [min1, min2, ...]
    }
    avgs = {
        'good' : None,
        'bad' : None
    }
    for group, devs in extensions.items():
        avg = dict()
        for dev, exts in devs.items():
            for ext, entropy in exts.items():
                if avg.get(ext) is None:
                    avg.update({ext: [entropy, set([dev]), entropy]}) # entropy sum, num of devs, avg
                else:
                    avg[ext][0] += entropy
                    avg[ext][1].add(dev)
                    avg[ext][2] = avg[ext][0]/len(avg[ext][1])
        avgs[group] = avg
        min = list()
        for e, data in avg.items():
            if data[2] < 0.6:
                if fpe[e] >= 100:
                    min.append((e, data[2]))
        # log_info(None, '{0[0]} min: {0[1]}.\n', (group, min))
        sorted_min = sorted(min, key=lambda x: x[1])
        extremes[group] = sorted_min
    log_info(None, 'extremes good are {0[0]} and bad are {0[1]}\n', (extremes['good'], extremes['bad']))
    compare_extremes(extremes, avgs)
    ext_difference(avgs)
    return extremes, avgs


def compare_extremes(extremes, avgs):
    """Compare the extremes (mins and maxs) against the entropy values for the other group."""
    opposites = {
        'good': list(),
        'bad' : list()
    }
    for group, exs in extremes.items():
        other_group = 'good' if group == 'bad' else 'bad'
        for ext in exs:
            if avgs[other_group].get(ext[0]) is None:
                continue
            ea = avgs[other_group].get(ext[0])[2]
            opposites[other_group].append([ext[0], ea])
    log_info(None, 'Corresponding values for extensions. Good: {0[0]}, Bad: {0[1]}.', (opposites['good'], opposites['bad']))
    return opposites


def ext_difference(avgs):
    """Find which extensions have the largest difference between two groups - good and bad."""
    ld = [None, 0, None, 0] # largest difference
    # for group, exts in avgs.items():
    other_group = 'bad'
    exts = avgs['good']
    for ext, values in exts.items():
        ae = values[2] # avg entropy
        opposite = avgs[other_group].get(ext)
        if opposite is None:
            continue
        difference = abs(ae - opposite[2])
        if difference > ld[1]:
            ld[0] = ext
            ld[1] = difference
        elif difference > ld[3]:
            ld[2] = ext
            ld[3] = difference
    log_info(None, 'Largest difference is {0[0]}.', (ld,))
    return ld


def analyze_group_exts():
    """Get entropy by extension for a group and find the min.
    It's an alternative method to the average extension entropy values."""
    days = {'good': load_data('data/days_good.json'), 'bad': load_data('data/days_bad.json')}
    entropies = {'good': dict(), 'bad': dict()}
    for g, data in days.items():
        for dev, dates in data.items():
            uniques = get_unique_extensions(dates)
            for ext, ds in uniques.items():
                if entropies[g].get(ext) is None:
                    entropies[g].update({ext: list(ds)})
                else:
                    entropies[g][ext].extend(list(ds))
    for group, d in entropies.items():
        for extension, dys in d.items():
            e = 0
            for day in dys:
                p_x = float(day[1].count(extension)) / len(day[1])
                if p_x > 0:
                    e -= p_x * math.log(p_x, 2)
            entropies[group][extension] = e
    for gp, da in entropies.items():
        min = list()
        for et, x in da.items():
            if x == 0:
                min.append(et)
        log_info(None, 'Extension entropy mins for {0[0]} are: {0[1]}', (gp, min))


def get_ranges(devs):
    """Get entropy ranges over 4 years."""
    focus_level = [0, 0] # [focused, NF]
    focused_limit = 1
    ranges = {0.001: 0, 0.01: 0, 0.1: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 }
    bottom = 0
    categories = list()
    for c in list(ranges.keys()):
        if bottom == 0:
            category = str(bottom) + '-' + str(c)
            categories.append(category)
            bottom = c + 0.0001
        else:
            category = str(bottom) + '-' + str(c)
            categories.append(category)
            bottom = c + 0.001
    for dev in devs:
        # focus level
        if dev[1] <= focused_limit:
            focus_level[0] += 1
        else:
            focus_level[1] += 1
        # ranges
        for limit in list(ranges.keys()):
            if dev[1] <= limit:
                ranges[limit] += 1
                break
    rs = [y for x, y in ranges.items()]
    return ranges, rs, categories, focus_level


def get_ext_file_nums(groups):
    extensions = dict()
    for g, authors in groups.items():
        for dev, dates in authors.items():
            for date, info in dates.items():
                for c in info['commits']:
                    for sha, files in c.items():
                        fs = [x['new'] for x in files]
                        exts = extract_extentions(fs)
                        for e in exts:
                            if extensions.get(e) is None:
                                extensions.update({e : 1})
                            else:
                                extensions[e] +=1
    return extensions


def get_focus():
    os.makedirs('data/test', exist_ok=True)
    groups = set_up_groups()
    fpe = get_ext_file_nums(groups) # files per extension
    save_in_file(groups, 'entropy_groups.json', 'data')
    ratios = load_ratios()
    T1 = time()
    ## focus analysis - daily, weekly, yearly, 4 years
    analyze_extensions(groups, ratios)
    compare_weeks_daily_sums()
    ## focus analysis per extension
    ext = extensions_entropies()
    save_in_file(ext, 'entropy_extensions.json', 'data')
    average_ext_number(ext)
    distribution = extension_distribution(ext)
    save_in_file(distribution, 'entropy_ext_distribution.json', 'data')
    get_ext_ranges(ext)
    popular = compare_most_popular(ext)
    save_in_file(popular, 'entropy_exts_popular.json', 'data')
    get_extremes_avg(ext, fpe)
    # analyze_group_exts()
    log_debug(None, 'Extensions analyzed in {0[0]} seconds', (time() - T1,))


def main():
    get_focus()


if __name__ == '__main__':
    main()