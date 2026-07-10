from django.core.management.base import BaseCommand
from core.models import SHSStream, Subject, SHSStreamSubject, Interest


class Command(BaseCommand):
    help = 'Seeds initial SHS streams, subjects, and interests'

    def handle(self, *args, **options):
        self.stdout.write('Seeding data...')

        # ── Interests ──
        interests_data = ['Coding', 'Making Games', 'Construction', 'Gardening',
                          'Driving', 'Teacher', 'Electrician', 'Art', 'Drawing',
                          'Science', 'Business', 'Healthcare', 'Law', 'Engineering',
                          'Design', 'Music', 'Sports', 'Writing', 'Technology']
        interest_objs = {}
        for name in interests_data:
            obj, _ = Interest.objects.get_or_create(name=name)
            interest_objs[name] = obj
        self.stdout.write(f'  {len(interests_data)} interests')

        # ── Subjects ──
        subjects_data = [
            ('English Language', 'CORE'),
            ('Core Mathematics', 'CORE'),
            ('Integrated Science', 'CORE'),
            ('Social Studies', 'CORE'),
            ('Elective Mathematics', 'ELECTIVE'),
            ('Physics', 'ELECTIVE'),
            ('Chemistry', 'ELECTIVE'),
            ('Biology', 'ELECTIVE'),
            ('General Agriculture', 'ELECTIVE'),
            ('Geography', 'ELECTIVE'),
            ('ICT', 'ELECTIVE'),
            ('History', 'ELECTIVE'),
            ('Government', 'ELECTIVE'),
            ('Economics', 'ELECTIVE'),
            ('Literature in English', 'ELECTIVE'),
            ('French', 'ELECTIVE'),
            ('Ghanaian Language', 'ELECTIVE'),
            ('Christian Religious Studies', 'ELECTIVE'),
            ('Islamic Religious Studies', 'ELECTIVE'),
            ('Business Management', 'ELECTIVE'),
            ('Financial Accounting', 'ELECTIVE'),
            ('Cost Accounting', 'ELECTIVE'),
            ('General Knowledge in Art', 'ELECTIVE'),
            ('Graphic Design', 'ELECTIVE'),
            ('Picture Making', 'ELECTIVE'),
            ('Textiles', 'ELECTIVE'),
            ('Ceramics', 'ELECTIVE'),
            ('Sculpture', 'ELECTIVE'),
            ('Management in Living', 'ELECTIVE'),
            ('Food and Nutrition', 'ELECTIVE'),
            ('Clothing and Textiles', 'ELECTIVE'),
            ('Animal Husbandry', 'ELECTIVE'),
            ('Crop Husbandry', 'ELECTIVE'),
            ('Technical Drawing', 'ELECTIVE'),
            ('Applied Electricity', 'ELECTIVE'),
            ('Electronics', 'ELECTIVE'),
            ('Building Construction', 'ELECTIVE'),
            ('Metalwork', 'ELECTIVE'),
            ('Woodwork', 'ELECTIVE'),
            ('Robotics', 'ELECTIVE'),
        ]
        subject_objs = {}
        for name, cat in subjects_data:
            obj, _ = Subject.objects.get_or_create(name=name, category=cat)
            subject_objs[name] = obj
        self.stdout.write(f'  {len(subjects_data)} subjects')

        # ── SHS Streams ──
        streams_data = [
            {
                'name': 'General Science',
                'slug': 'general-science',
                'description': 'The most rigorous SHS pathway, focused on foundational sciences for medicine, engineering, and computing.',
                'strengths': 'Quantitative reasoning, Analytical thinking, Problem-solving, Experimental skills',
                'subjects': [
                    ('English Language', True), ('Core Mathematics', True),
                    ('Integrated Science', True), ('Social Studies', True),
                    ('Biology', False), ('Chemistry', False),
                    ('Physics', False), ('Elective Mathematics', False),
                    ('General Agriculture', False), ('Geography', False), ('ICT', False),
                ],
            },
            {
                'name': 'General Arts',
                'slug': 'general-arts',
                'description': 'The most versatile programme, offering pathways into law, social sciences, humanities, and education.',
                'strengths': 'Verbal/linguistic skills, Social analysis, Critical thinking, Writing',
                'subjects': [
                    ('English Language', True), ('Core Mathematics', True),
                    ('Integrated Science', True), ('Social Studies', True),
                    ('History', False), ('Government', False),
                    ('Economics', False), ('Geography', False),
                    ('Literature in English', False), ('French', False),
                    ('Ghanaian Language', False), ('Christian Religious Studies', False),
                    ('Islamic Religious Studies', False), ('ICT', False),
                ],
            },
            {
                'name': 'Business',
                'slug': 'business',
                'description': 'Tailored for careers in the corporate sector, finance, banking, and organizational management.',
                'strengths': 'Financial thinking, Organizational logic, Numerical literacy, Administrative reasoning',
                'subjects': [
                    ('English Language', True), ('Core Mathematics', True),
                    ('Integrated Science', True), ('Social Studies', True),
                    ('Business Management', False), ('Financial Accounting', False),
                    ('Cost Accounting', False), ('Economics', False),
                    ('Elective Mathematics', False), ('ICT', False),
                ],
            },
            {
                'name': 'Visual Arts',
                'slug': 'visual-arts',
                'description': 'Fosters creativity, aesthetic theory, and practical design skills for the built environment and digital media.',
                'strengths': 'Creative thinking, Visual communication, Design skills, Spatial awareness',
                'subjects': [
                    ('English Language', True), ('Core Mathematics', True),
                    ('Integrated Science', True), ('Social Studies', True),
                    ('General Knowledge in Art', False), ('Graphic Design', False),
                    ('Picture Making', False), ('Textiles', False),
                    ('Ceramics', False), ('Sculpture', False),
                    ('Economics', False), ('ICT', False),
                ],
            },
            {
                'name': 'Home Economics',
                'slug': 'home-economics',
                'description': 'Focused on domestic science, hospitality, nutrition, and early childhood development.',
                'strengths': 'Practical skills, Scientific application in domestic contexts, Attention to detail',
                'subjects': [
                    ('English Language', True), ('Core Mathematics', True),
                    ('Integrated Science', True), ('Social Studies', True),
                    ('Management in Living', False), ('Food and Nutrition', False),
                    ('Clothing and Textiles', False), ('General Knowledge in Art', False),
                    ('Economics', False), ('Biology', False), ('Chemistry', False),
                ],
            },
            {
                'name': 'Agricultural Science',
                'slug': 'agricultural-science',
                'description': 'Merges scientific theory with practical agricultural mechanics, animal science, and economics.',
                'strengths': 'Scientific reasoning, Practical application, Environmental awareness',
                'subjects': [
                    ('English Language', True), ('Core Mathematics', True),
                    ('Integrated Science', True), ('Social Studies', True),
                    ('General Agriculture', False), ('Animal Husbandry', False),
                    ('Crop Husbandry', False), ('Chemistry', False),
                    ('Physics', False), ('Elective Mathematics', False),
                    ('Economics', False), ('ICT', False),
                ],
            },
            {
                'name': 'Technical / Vocational',
                'slug': 'technical',
                'description': 'Geared toward industrial, mechanical, and artisanal proficiency for TVET pathways.',
                'strengths': 'Practical/spatial reasoning, Mechanical aptitude, Procedural thinking',
                'subjects': [
                    ('English Language', True), ('Core Mathematics', True),
                    ('Integrated Science', True), ('Social Studies', True),
                    ('Technical Drawing', False), ('Applied Electricity', False),
                    ('Electronics', False), ('Building Construction', False),
                    ('Metalwork', False), ('Woodwork', False), ('ICT', False),
                    ('Physics', False),
                ],
            },
            {
                'name': 'STEM',
                'slug': 'stem',
                'description': 'Exclusive to STEM institutions, hyper-focused on modern technological and biomedical disciplines.',
                'strengths': 'Advanced calculus, Scientific inquiry, Engineering design, Computational thinking',
                'subjects': [
                    ('English Language', True), ('Core Mathematics', True),
                    ('Integrated Science', True), ('Social Studies', True),
                    ('Elective Mathematics', False), ('Physics', False),
                    ('Chemistry', False), ('Biology', False),
                    ('Robotics', False), ('ICT', False),
                ],
            },
        ]

        for sd in streams_data:
            stream, created = SHSStream.objects.get_or_create(
                slug=sd['slug'],
                defaults={
                    'name': sd['name'],
                    'description': sd['description'],
                    'strengths': sd['strengths'],
                }
            )
            for subj_name, is_core in sd['subjects']:
                if subj_name in subject_objs:
                    SHSStreamSubject.objects.get_or_create(
                        stream=stream,
                        subject=subject_objs[subj_name],
                        defaults={'is_core': is_core}
                    )
            self.stdout.write(f'  Stream: {stream.name}')

        self.stdout.write(self.style.SUCCESS('Done! Data seeded successfully.'))
