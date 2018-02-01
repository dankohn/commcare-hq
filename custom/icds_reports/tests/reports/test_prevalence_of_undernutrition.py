from __future__ import absolute_import
from collections import OrderedDict

from django.test.utils import override_settings

from custom.icds_reports.const import ChartColors, MapColors
from custom.icds_reports.reports.prevalence_of_undernutrition import get_prevalence_of_undernutrition_data_map, \
    get_prevalence_of_undernutrition_data_chart, get_prevalence_of_undernutrition_sector_data
from django.test import TestCase


@override_settings(SERVER_ENVIRONMENT='icds')
class TestPrevalenceOfUndernutrition(TestCase):
    maxDiff = None

    def test_map_data_keys(self):
        data = get_prevalence_of_undernutrition_data_map(
            'icds-cas',
            config={
                'month': (2017, 5, 1),
            },
            loc_level='state'
        )
        self.assertEquals(len(data), 5)
        self.assertIn('rightLegend', data)
        self.assertIn('fills', data)
        self.assertIn('data', data)
        self.assertIn('slug', data)
        self.assertIn('label', data)

    def test_map_data_right_legend_keys(self):
        data = get_prevalence_of_undernutrition_data_map(
            'icds-cas',
            config={
                'month': (2017, 5, 1),
            },
            loc_level='state'
        )['rightLegend']
        self.assertEquals(len(data), 3)
        self.assertIn('info', data)
        self.assertIn('average', data)
        self.assertIn('extended_info', data)

    def test_map_data(self):
        data = get_prevalence_of_undernutrition_data_map(
            'icds-cas',
            config={
                'month': (2017, 5, 1),
            },
            loc_level='state'
        )
        self.assertDictEqual(
            data['data'],
            {
                'st1': {
                    'total': 1585,
                    'severely_underweight': 40,
                    'moderately_underweight': 320,
                    'fillKey': '20%-35%',
                    'original_name': ["st1"],
                    'normal': 1225
                },
                'st2': {
                    'total': 1895,
                    'severely_underweight': 60,
                    'moderately_underweight': 330,
                    'original_name': ["st2"],
                    'fillKey': '20%-35%',
                    'normal': 1505
                }
            }
        )

    def test_map_data_right_legend_info(self):
        data = get_prevalence_of_undernutrition_data_map(
            'icds-cas',
            config={
                'month': (2017, 5, 1),
            },
            loc_level='state'
        )
        expected = (
            u'Percentage of children between 0 - 5 years enrolled for Anganwadi Services'
            u' with weight-for-age less than -2 standard deviations'
            u' of the WHO Child Growth Standards median.'
            u' <br/><br/>Children who are moderately or severely underweight'
            u' have a higher risk of mortality'
        )
        self.assertEquals(data['rightLegend']['info'], expected)

    def test_map_data_right_legend_average(self):
        data = get_prevalence_of_undernutrition_data_map(
            'icds-cas',
            config={
                'month': (2017, 5, 1),
            },
            loc_level='state'
        )
        self.assertEquals(data['rightLegend']['average'], 21.64670434399008)

    def test_map_data_right_legend_extended_info(self):
        data = get_prevalence_of_undernutrition_data_map(
            'icds-cas',
            config={
                'month': (2017, 5, 1),
            },
            loc_level='state'
        )
        self.assertListEqual(
            data['rightLegend']['extended_info'],
            [
                {'indicator': 'Total Children (0 - 5 years) weighed in given month:', 'value': '3,480'},
                {'indicator': '% Unweighed (0 - 5 years):', 'value': '29.63%'},
                {'indicator': '% Severely Underweight (0 - 5 years):', 'value': '2.87%'},
                {'indicator': '% Moderately Underweight (0 - 5 years):', 'value': '18.68%'},
                {'indicator': '% Normal (0 - 5 years):', 'value': '78.45%'}
            ]
        )

    def test_map_data_fills(self):
        data = get_prevalence_of_undernutrition_data_map(
            'icds-cas',
            config={
                'month': (2017, 5, 1),
            },
            loc_level='state'
        )
        self.assertDictEqual(
            data['fills'],
            {
                "0%-20%": MapColors.PINK,
                "20%-35%": MapColors.ORANGE,
                "35%-100%": MapColors.RED,
                "defaultFill": MapColors.GREY
            }
        )

    def test_map_data_slug(self):
        data = get_prevalence_of_undernutrition_data_map(
            'icds-cas',
            config={
                'month': (2017, 5, 1),
            },
            loc_level='state'
        )
        self.assertEquals(data['slug'], 'moderately_underweight')

    def test_map_data_label(self):
        data = get_prevalence_of_undernutrition_data_map(
            'icds-cas',
            config={
                'month': (2017, 5, 1),
            },
            loc_level='state'
        )
        self.assertEquals(data['label'], 'Percent of Children Underweight (0 - 5 years)')

    def test_map_name_two_locations_represent_by_one_topojson(self):
        data = get_prevalence_of_undernutrition_data_map(
            'icds-cas',
            config={
                'month': (2017, 5, 1),
                'state_id': 'st1',
                'district_id': 'd1',
                'aggregation_level': 3
            },
            loc_level='block',
        )
        self.assertDictEqual(
            data['data'],
            {
                'block_map': {
                    'severely_underweight': 8,
                    'moderately_underweight': 64,
                    'normal': 245,
                    'total': 317,
                    'original_name': ['b1', 'b2'],
                    'fillKey': '20%-35%'
                }
            }
        )

    def test_average_with_two_locations_represent_by_one_topojson(self):
        data = get_prevalence_of_undernutrition_data_map(
            'icds-cas',
            config={
                'month': (2017, 5, 1),
                'state_id': 'st1',
                'district_id': 'd1',
                'aggregation_level': 3
            },
            loc_level='block',
        )
        self.assertEquals(data['rightLegend']['average'], 22.743014091234773)

    def test_chart_data(self):
        self.assertDictEqual(
            get_prevalence_of_undernutrition_data_chart(
                'icds-cas',
                config={
                    'month': (2017, 5, 1)
                },
                loc_level='state'
            ),
            {
                "location_type": "State",
                "bottom_five": [
                    {
                        "loc_name": "st1",
                        "percent": 15.157894736842104
                    },
                    {
                        "loc_name": "st2",
                        "percent": 15.17509727626459
                    },
                ],
                "top_five": [
                    {
                        "loc_name": "st1",
                        "percent": 15.157894736842104
                    },
                    {
                        "loc_name": "st2",
                        "percent": 15.17509727626459
                    },
                ],
                "chart_data": [
                    {
                        "color": ChartColors.PINK,
                        "classed": "dashed",
                        "strokeWidth": 2,
                        "values": [
                            {
                                "y": 0.0,
                                "x": 1485907200000,
                                "all": 0
                            },
                            {
                                "y": 0.0,
                                "x": 1488326400000,
                                "all": 0
                            },
                            {
                                "y": 0.5048923679060665,
                                "x": 1491004800000,
                                "all": 5110
                            },
                            {
                                "y": 0.5520728008088979,
                                "x": 1493596800000,
                                "all": 4945
                            }
                        ],
                        "key": "% Normal"
                    },
                    {
                        "color": ChartColors.ORANGE,
                        "classed": "dashed",
                        "strokeWidth": 2,
                        "values": [
                            {
                                "y": 0.0,
                                "x": 1485907200000,
                                "all": 0
                            },
                            {
                                "y": 0.0,
                                "x": 1488326400000,
                                "all": 0
                            },
                            {
                                "y": 0.15655577299412915,
                                "x": 1491004800000,
                                "all": 5110
                            },
                            {
                                "y": 0.13144590495449948,
                                "x": 1493596800000,
                                "all": 4945
                            }
                        ],
                        "key": "% Moderately Underweight (-2 SD)"
                    },
                    {
                        "color": ChartColors.RED,
                        "classed": "dashed",
                        "strokeWidth": 2,
                        "values": [
                            {
                                "y": 0.0,
                                "x": 1485907200000,
                                "all": 0
                            },
                            {
                                "y": 0.0,
                                "x": 1488326400000,
                                "all": 0
                            },
                            {
                                "y": 0.014677103718199608,
                                "x": 1491004800000,
                                "all": 5110
                            },
                            {
                                "y": 0.020222446916076844,
                                "x": 1493596800000,
                                "all": 4945
                            }
                        ],
                        "key": "% Severely Underweight (-3 SD) "
                    }
                ],
                "all_locations": [
                    {
                        "loc_name": "st1",
                        "percent": 15.157894736842104
                    },
                    {
                        "loc_name": "st2",
                        "percent": 15.17509727626459
                    },
                ]
            }
        )

    def test_sector_data(self):
        self.assertDictEqual(
            get_prevalence_of_undernutrition_sector_data(
                'icds-cas',
                config={
                    'month': (2017, 5, 1),
                    'state_id': 'st1',
                    'district_id': 'd1',
                    'block_id': 'b1',
                },
                location_id='b1',
                loc_level='supervisor'
            ),
            {
                "info": "Percentage of children between 0-5 years enrolled for Anganwadi Services with "
                        "weight-for-age less than -2 standard deviations of the WHO Child Growth Standards median."
                        " <br/><br/>Children who are moderately "
                        "or severely underweight have a higher risk of mortality",
                "tooltips_data": {
                    u"s2": {
                        "total": 182,
                        "severely_underweight": 4,
                        "moderately_underweight": 54,
                        "normal": 124
                    },
                    u"s1": {
                        "total": 134,
                        "severely_underweight": 8,
                        "moderately_underweight": 36,
                        "normal": 90
                    },
                    None: {
                        "total": 158,
                        "severely_underweight": 6,
                        "moderately_underweight": 45,
                        "normal": 107
                    }
                },
                "chart_data": [
                    {
                        "color": MapColors.BLUE,
                        "classed": "dashed",
                        "strokeWidth": 2,
                        "values": [
                            [
                                None,
                                0.3227848101265823
                            ],
                            [
                                "s1",
                                0.3283582089552239
                            ],
                            [
                                "s2",
                                0.31868131868131866
                            ]
                        ],
                        "key": ""
                    }
                ]
            }
        )
