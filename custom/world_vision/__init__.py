from custom.world_vision.reports.child_report import ChildTTCReport
from custom.world_vision.reports.mixed_report import MixedTTCReport
from custom.world_vision.reports.mother_report import MotherTTCReport

DEFAULT_URL = MixedTTCReport

WORLD_VISION_DOMAINS = ('wvindia2', )

CUSTOM_REPORTS = (
    ('TTC App Reports', (
        MixedTTCReport,
        MotherTTCReport,
        ChildTTCReport
    )),
)

REASON_FOR_CLOSURE_MAPPING = {
    'change_of_location': 'Migration',
    'end_of_care': 'End of care',
    'end_of_pregnancy': 'End of care (Postpartum Completed)',
    'not_pregnant': 'Not Pregnant (mostly  incorrect registrations)',
    'abortion': 'Abortion',
    'death': 'Death'
}

MOTHER_DEATH_MAPPING = {
    'seizure': 'Seizure or fits',
    'high_bp': 'High blood pressure',
    'bleeding_postpartum': 'Excessive bleeding post-delivery',
    'fever_or_infection_post_delivery': 'Fever or infection post-delivery',
    'during_caeserian_surgery': 'During Caeserian Surgery',
    'other': 'Other reason'
}
