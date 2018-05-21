import pygal


def create_chart(data, high_score_first=False, style='compare'):
    """
    Generate line charts from a dictionary-like objects

    :param data:
    data expected to be a dictionary-like objects of the following form:
    test_chart = {
        'columns': ['TT', 'SWI'],
        'title': 'title',
        'little joe': [12, 15],
        'tiny joe': [10, 20],
    }
    high_score_first is a boolean used to invert the y axis to show low positions first (for single events)

    :return:
    return data is an svg chart of the results
    """
    from pygal.style import DarkStyle
    custom_dark_style = DarkStyle(transition='50ms')
    chart = pygal.Line(inverse_y_axis=high_score_first, style=custom_dark_style)
    chart.title = data['title']
    chart.x_labels = [col for col in data['columns']]
    # Rider name followed by point totals
    lines = [[rider] + [point_total for point_total in data[rider]] for rider in data if rider not in ['title', 'columns']]
    for line in lines:
        chart.add(line[0], line[1:])
    chart = chart.render()
    return chart


if __name__ == '__main__':
    import sys
    import os
    import django

    sys.path.append('gpstats')
    os.environ['DJANGO_SETTINGS_MODULE'] = 'gpstats.settings'
    django.setup()

    test_chart = {
        'columns': ['TT', 'SWI'],
        'title': '1900',
        'Joe Blow': [25, 25],
        'Joe Schmoe': [0, 25],
        }
    create_chart(test_chart)
