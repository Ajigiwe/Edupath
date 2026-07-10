from django.core.management.base import BaseCommand
from core.models import (
    SHSStream, Subject, Interest, Program, ProgramDetails,
    Institution, InstitutionType, Ownership, Level,
    ProgramPrerequisite, ProgramAdmissionTier, AlternativePathway
)


def goc(model, **kwargs):
    obj, created = model.objects.get_or_create(**kwargs)
    return obj


class Command(BaseCommand):
    help = 'Seeds real institution cutoff data from the Ghana Educational Landscape document'

    def handle(self, *args, **options):
        self.stdout.write('Seeding institution and cutoff data...')

        # ── Ensure reference records ──
        govt_own = goc(Ownership, name='Government')
        priv_own = goc(Ownership, name='Private')

        uni_type = goc(InstitutionType, typename='Public University', ownership=govt_own)
        tech_uni_type = goc(InstitutionType, typename='Technical University', ownership=govt_own)
        priv_uni_type = goc(InstitutionType, typename='Private University', ownership=priv_own)
        health_uni_type = goc(InstitutionType, typename='Health Sciences University', ownership=govt_own)
        prof_uni_type = goc(InstitutionType, typename='Professional University', ownership=govt_own)
        spec_uni_type = goc(InstitutionType, typename='Specialized Public University', ownership=govt_own)

        deg_level = goc(Level, levelsname='Degree')
        dip_level = goc(Level, levelsname='Diploma')
        hnd_level = goc(Level, levelsname='High National Diploma')
        cert_level = goc(Level, levelsname='Certificate')

        # ── Subject lookups ──
        def subj(name):
            return Subject.objects.get(name=name)

        S = {
            'math': subj('Core Mathematics'),
            'eng': subj('English Language'),
            'sci': subj('Integrated Science'),
            'soc': subj('Social Studies'),
            'emath': subj('Elective Mathematics'),
            'physics': subj('Physics'),
            'chem': subj('Chemistry'),
            'bio': subj('Biology'),
            'geo': subj('Geography'),
            'ict': subj('ICT'),
            'hist': subj('History'),
            'govt': subj('Government'),
            'econ': subj('Economics'),
            'lit': subj('Literature in English'),
            'acct': subj('Financial Accounting'),
            'biz_mgmt': subj('Business Management'),
            'costing': subj('Cost Accounting'),
            'td': subj('Technical Drawing'),
            'ae': subj('Applied Electricity'),
            'elec': subj('Electronics'),
            'gkart': subj('General Knowledge in Art'),
        }

        # ── Interest lookups ──
        def intr(name):
            return Interest.objects.get(name=name)

        I = {
            'coding': intr('Coding'),
            'games': intr('Making Games'),
            'construction': intr('Construction'),
            'gardening': intr('Gardening'),
            'driving': intr('Driving'),
            'teacher': intr('Teacher'),
            'electrician': intr('Electrician'),
            'art': intr('Art'),
            'drawing': intr('Drawing'),
            'science': intr('Science'),
            'business': intr('Business'),
            'healthcare': intr('Healthcare'),
            'law': intr('Law'),
            'engineering': intr('Engineering'),
            'design': intr('Design'),
            'music': intr('Music'),
            'sports': intr('Sports'),
            'writing': intr('Writing'),
            'technology': intr('Technology'),
        }

        # ════════════════════════════════════════════
        # INSTITUTIONS
        # ════════════════════════════════════════════

        institutions = {}

        def make_institution(name, itype, level, location, phone='0000000000'):
            nonlocal institutions
            inst, _ = Institution.objects.get_or_create(
                institutionname=name,
                defaults={
                    'institutiontype': itype,
                    'level': level,
                    'location': location,
                    'phonenumber': phone,
                }
            )
            institutions[name] = inst
            return inst

        make_institution('University of Ghana', uni_type, deg_level, 'Legon, Accra')
        make_institution('Kwame Nkrumah University of Science and Technology', uni_type, deg_level, 'Kumasi')
        make_institution('University of Cape Coast', uni_type, deg_level, 'Cape Coast')
        make_institution('University for Development Studies', uni_type, deg_level, 'Tamale')
        make_institution('University of Health and Allied Sciences', health_uni_type, deg_level, 'Ho')
        make_institution('University of Professional Studies, Accra', prof_uni_type, deg_level, 'Accra')
        make_institution('University of Mines and Technology', uni_type, deg_level, 'Tarkwa')
        make_institution('University of Education, Winneba', uni_type, deg_level, 'Winneba')
        make_institution('University of Energy and Natural Resources', uni_type, deg_level, 'Sunyani')
        # ── Technical Universities ──
        make_institution('Accra Technical University', tech_uni_type, deg_level, 'Accra')
        make_institution('Takoradi Technical University', tech_uni_type, deg_level, 'Takoradi')
        make_institution('Kumasi Technical University', tech_uni_type, deg_level, 'Kumasi')
        make_institution('Cape Coast Technical University', tech_uni_type, deg_level, 'Cape Coast')
        make_institution('Koforidua Technical University', tech_uni_type, deg_level, 'Koforidua')
        make_institution('Ho Technical University', tech_uni_type, deg_level, 'Ho')
        make_institution('Tamale Technical University', tech_uni_type, deg_level, 'Tamale')
        make_institution('Sunyani Technical University', tech_uni_type, deg_level, 'Sunyani')
        make_institution('Bolgatanga Technical University', tech_uni_type, deg_level, 'Bolgatanga')
        make_institution('Wa Technical University', tech_uni_type, deg_level, 'Wa')

        # ── Private Universities ──
        make_institution('Ashesi University', priv_uni_type, deg_level, 'Berekuso')
        make_institution('Central University', priv_uni_type, deg_level, 'Miotso')
        make_institution('Valley View University', priv_uni_type, deg_level, 'Oyibi, Accra')
        make_institution('Lancaster University Ghana', priv_uni_type, deg_level, 'Accra')

        self.stdout.write(f'  {len(institutions)} institutions')

        # ════════════════════════════════════════════
        # PROGRAMS
        # ════════════════════════════════════════════

        programs = {}

        def make_program(name, interests_list):
            p, _ = Program.objects.get_or_create(programname=name)
            for i in interests_list:
                p.interests.add(i)
            programs[name] = p
            return p

        make_program('Medicine and Surgery', [I['healthcare'], I['science']])
        make_program('Dental Surgery', [I['healthcare'], I['science']])
        make_program('Pharmacy', [I['healthcare'], I['science']])
        make_program('Nursing', [I['healthcare'], I['science']])
        make_program('Midwifery', [I['healthcare']])
        make_program('Medical Laboratory Science', [I['healthcare'], I['science']])
        make_program('Biomedical Engineering', [I['engineering'], I['science'], I['healthcare']])
        make_program('Computer Engineering', [I['engineering'], I['coding'], I['technology']])
        make_program('Computer Science', [I['coding'], I['technology'], I['games']])
        make_program('Information Technology', [I['coding'], I['technology']])
        make_program('Software Engineering', [I['coding'], I['technology']])
        make_program('Data Science', [I['coding'], I['technology'], I['science']])
        make_program('Cyber Security', [I['coding'], I['technology']])
        make_program('Actuarial Science', [I['science'], I['business']])
        make_program('Mathematics', [I['science'], I['teacher']])
        make_program('Statistics', [I['science'], I['business']])
        make_program('Physics', [I['science']])
        make_program('Chemistry', [I['science']])
        make_program('Biology', [I['science']])
        make_program('Biological Sciences', [I['science'], I['healthcare']])
        make_program('Veterinary Medicine', [I['science'], I['healthcare'], I['gardening']])
        make_program('Agriculture', [I['gardening'], I['science']])
        make_program('Agricultural Engineering', [I['gardening'], I['engineering']])
        make_program('Civil Engineering', [I['construction'], I['engineering']])
        make_program('Mechanical Engineering', [I['engineering']])
        make_program('Electrical and Electronic Engineering', [I['engineering'], I['electrician']])
        make_program('Chemical Engineering', [I['engineering'], I['science']])
        make_program('Petroleum Engineering', [I['engineering'], I['science']])
        make_program('Mining Engineering', [I['engineering']])
        make_program('Aerospace Engineering', [I['engineering'], I['technology']])
        make_program('Marine Engineering', [I['engineering']])
        make_program('Industrial Engineering', [I['engineering'], I['business']])
        make_program('Materials Engineering', [I['engineering'], I['science']])
        make_program('Environmental Science', [I['science'], I['gardening']])
        make_program('Architecture', [I['design'], I['art'], I['drawing']])
        make_program('Construction Technology and Management', [I['construction'], I['engineering']])
        make_program('Quantity Surveying and Construction Economics', [I['construction'], I['business']])
        make_program('Land Economy', [I['business'], I['construction']])
        make_program('Law', [I['law'], I['writing'], I['teacher']])
        make_program('Business Administration', [I['business']])
        make_program('Accounting', [I['business']])
        make_program('Finance', [I['business']])
        make_program('Banking and Finance', [I['business']])
        make_program('Human Resource Management', [I['business']])
        make_program('Marketing', [I['business'], I['writing']])
        make_program('Public Relations Management', [I['writing'], I['business']])
        make_program('Economics', [I['science'], I['business']])
        make_program('Communication Studies', [I['writing'], I['art']])
        make_program('Political Science', [I['writing'], I['teacher']])
        make_program('Psychology', [I['science'], I['teacher']])
        make_program('Public Health', [I['healthcare'], I['science']])
        make_program('Dietetics', [I['healthcare'], I['science']])
        make_program('Physiotherapy', [I['healthcare'], I['science']])
        make_program('Diagnostic Imaging (Radiography)', [I['healthcare'], I['science']])
        make_program('Optometry', [I['healthcare'], I['science']])
        make_program('Education (Science)', [I['teacher'], I['science']])
        make_program('Education (Arts)', [I['teacher'], I['writing']])
        make_program('Education (Mathematics)', [I['teacher'], I['science']])
        make_program('Education (Early Childhood)', [I['teacher']])
        make_program('Actuarial Science', [I['business'], I['science']])
        make_program('Fine Arts', [I['art'], I['drawing'], I['design']])
        make_program('Communication Design', [I['design'], I['art'], I['writing']])
        make_program('Hospitality Management', [I['business'], I['drawing']])
        make_program('Food Process Engineering', [I['engineering'], I['science'], I['gardening']])
        make_program('Renewable Energy Engineering', [I['engineering'], I['science'], I['gardening']])
        make_program('Geomatic Engineering', [I['engineering'], I['construction']])
        make_program('Earth Science', [I['science'], I['gardening']])
        make_program('Occupational Therapy', [I['healthcare'], I['science']])
        make_program('Building Technology', [I['construction'], I['engineering']])
        make_program('Fashion Design and Textiles', [I['design'], I['art']])
        make_program('Tourism Management', [I['business'], I['drawing']])
        make_program('Computer Technology', [I['coding'], I['technology']])
        make_program('Food Technology', [I['science'], I['gardening']])
        make_program('Pharmaceutical Sciences', [I['healthcare'], I['science']])
        make_program('Architectural Technology', [I['construction'], I['design'], I['art']])
        make_program('Interior Design Technology', [I['design'], I['art']])
        make_program('Laboratory Technology', [I['science'], I['healthcare']])
        make_program('Dispensing Technology', [I['healthcare']])
        make_program('Statistics', [I['science'], I['business']])
        make_program('Purchasing and Supply', [I['business']])
        make_program('Estate Management', [I['business'], I['construction']])
        make_program('Agribusiness', [I['business'], I['gardening']])
        make_program('Entrepreneurship', [I['business']])
        make_program('Biostatistics', [I['science'], I['healthcare']])
        make_program('Procurement and Supply Chain Management', [I['business']])
        make_program('Automotive Engineering', [I['engineering']])
        make_program('Oil and Gas Engineering', [I['engineering'], I['science']])
        make_program('Mechatronics Engineering', [I['engineering'], I['technology']])

        self.stdout.write(f'  {len(programs)} programs')

        # ════════════════════════════════════════════
        # PROGRAM PREREQUISITES
        # ════════════════════════════════════════════

        prereq_data = {
            'Medicine and Surgery': [('REQ', S['bio'], 4), ('REQ', S['chem'], 4), ('PRE', S['physics'], 6),
                                      ('PRE', S['emath'], 6), ('NIC', S['eng'], 6)],
            'Dental Surgery': [('REQ', S['bio'], 4), ('REQ', S['chem'], 4), ('PRE', S['physics'], 6),
                                ('PRE', S['emath'], 6)],
            'Pharmacy': [('REQ', S['bio'], 4), ('REQ', S['chem'], 4), ('PRE', S['physics'], 6),
                          ('PRE', S['emath'], 6)],
            'Nursing': [('REQ', S['bio'], 6), ('PRE', S['chem'], 6), ('NIC', S['eng'], 6), ('NIC', S['math'], 6)],
            'Midwifery': [('REQ', S['bio'], 6), ('PRE', S['chem'], 6), ('NIC', S['eng'], 6)],
            'Medical Laboratory Science': [('REQ', S['bio'], 4), ('REQ', S['chem'], 4), ('PRE', S['physics'], 6)],
            'Biomedical Engineering': [('REQ', S['emath'], 4), ('REQ', S['physics'], 4), ('PRE', S['chem'], 6)],
            'Computer Engineering': [('REQ', S['emath'], 4), ('REQ', S['physics'], 4), ('PRE', S['chem'], 6),
                                      ('NIC', S['ict'], 6)],
            'Computer Science': [('REQ', S['emath'], 4), ('PRE', S['physics'], 6),
                                  ('PRE', S['eng'], 4), ('NIC', S['ict'], 6)],
            'Information Technology': [('PRE', S['emath'], 6), ('REQ', S['eng'], 4), ('NIC', S['ict'], 6)],
            'Software Engineering': [('REQ', S['emath'], 4), ('PRE', S['physics'], 6), ('NIC', S['ict'], 6)],
            'Data Science': [('REQ', S['emath'], 4), ('PRE', S['physics'], 6), ('NIC', S['ict'], 6),
                              ('PRE', S['eng'], 4)],
            'Cyber Security': [('REQ', S['emath'], 6), ('PRE', S['physics'], 6), ('NIC', S['ict'], 6),
                                ('PRE', S['eng'], 4)],
            'Actuarial Science': [('REQ', S['emath'], 4), ('PRE', S['econ'], 6), ('PRE', S['eng'], 4)],
            'Mathematics': [('REQ', S['emath'], 4), ('PRE', S['physics'], 6)],
            'Statistics': [('REQ', S['emath'], 4), ('PRE', S['physics'], 6)],
            'Physics': [('REQ', S['physics'], 4), ('REQ', S['emath'], 4), ('PRE', S['chem'], 6)],
            'Chemistry': [('REQ', S['chem'], 4), ('REQ', S['emath'], 4), ('PRE', S['physics'], 6)],
            'Biology': [('REQ', S['bio'], 4), ('PRE', S['chem'], 6), ('PRE', S['physics'], 6)],
            'Biological Sciences': [('REQ', S['bio'], 6), ('REQ', S['chem'], 6), ('PRE', S['physics'], 6)],
            'Veterinary Medicine': [('REQ', S['bio'], 4), ('REQ', S['chem'], 4), ('PRE', S['emath'], 6),
                                     ('PRE', S['physics'], 6)],
            'Agriculture': [('REQ', S['chem'], 6), ('PRE', S['bio'], 6), ('PRE', S['emath'], 6)],
            'Agricultural Engineering': [('REQ', S['emath'], 4), ('REQ', S['physics'], 4), ('PRE', S['chem'], 6)],
            'Civil Engineering': [('REQ', S['emath'], 4), ('REQ', S['physics'], 4), ('PRE', S['chem'], 6)],
            'Mechanical Engineering': [('REQ', S['emath'], 4), ('REQ', S['physics'], 4), ('PRE', S['chem'], 6)],
            'Electrical and Electronic Engineering': [('REQ', S['emath'], 4), ('REQ', S['physics'], 4),
                                                       ('PRE', S['chem'], 6)],
            'Chemical Engineering': [('REQ', S['emath'], 4), ('REQ', S['physics'], 4), ('REQ', S['chem'], 4)],
            'Petroleum Engineering': [('REQ', S['emath'], 4), ('REQ', S['physics'], 4), ('REQ', S['chem'], 4)],
            'Mining Engineering': [('REQ', S['emath'], 4), ('REQ', S['physics'], 4), ('PRE', S['chem'], 6)],
            'Aerospace Engineering': [('REQ', S['emath'], 4), ('REQ', S['physics'], 4)],
            'Marine Engineering': [('REQ', S['emath'], 6), ('REQ', S['physics'], 6), ('PRE', S['chem'], 6)],
            'Industrial Engineering': [('REQ', S['emath'], 4), ('REQ', S['physics'], 4), ('PRE', S['chem'], 6)],
            'Materials Engineering': [('REQ', S['emath'], 4), ('REQ', S['physics'], 4), ('REQ', S['chem'], 6)],
            'Environmental Science': [('REQ', S['chem'], 6), ('REQ', S['physics'], 6), ('PRE', S['bio'], 6),
                                       ('PRE', S['geo'], 6)],
            'Architecture': [('REQ', S['emath'], 6), ('REQ', S['physics'], 6), ('PRE', S['td'], 6),
                              ('PRE', S['gkart'], 6)],
            'Construction Technology and Management': [('REQ', S['emath'], 6), ('PRE', S['physics'], 6),
                                                        ('PRE', S['td'], 6)],
            'Quantity Surveying and Construction Economics': [('REQ', S['emath'], 6), ('PRE', S['physics'], 6),
                                                               ('PRE', S['td'], 6)],
            'Land Economy': [('REQ', S['emath'], 6), ('PRE', S['geo'], 6), ('PRE', S['econ'], 6)],
            'Law': [('REQ', S['eng'], 4), ('PRE', S['govt'], 6), ('PRE', S['hist'], 6), ('NIC', S['econ'], 6)],
            'Business Administration': [('REQ', S['eng'], 4), ('PRE', S['econ'], 6), ('PRE', S['emath'], 6)],
            'Accounting': [('REQ', S['acct'], 6), ('PRE', S['econ'], 6), ('PRE', S['emath'], 6), ('PRE', S['eng'], 4)],
            'Finance': [('REQ', S['econ'], 6), ('PRE', S['acct'], 6), ('PRE', S['emath'], 6), ('PRE', S['eng'], 4)],
            'Banking and Finance': [('REQ', S['econ'], 6), ('PRE', S['acct'], 6), ('PRE', S['emath'], 6),
                                     ('PRE', S['eng'], 4)],
            'Human Resource Management': [('REQ', S['eng'], 4), ('PRE', S['econ'], 6), ('PRE', S['biz_mgmt'], 6)],
            'Marketing': [('REQ', S['eng'], 4), ('PRE', S['econ'], 6), ('PRE', S['biz_mgmt'], 6)],
            'Public Relations Management': [('REQ', S['eng'], 4), ('PRE', S['govt'], 6)],
            'Economics': [('REQ', S['econ'], 6), ('PRE', S['emath'], 4), ('PRE', S['eng'], 4)],
            'Communication Studies': [('REQ', S['eng'], 4), ('PRE', S['lit'], 6), ('PRE', S['govt'], 6)],
            'Political Science': [('REQ', S['govt'], 6), ('PRE', S['hist'], 6), ('PRE', S['eng'], 4)],
            'Psychology': [('PRE', S['bio'], 6), ('PRE', S['emath'], 6), ('PRE', S['eng'], 4)],
            'Public Health': [('REQ', S['bio'], 6), ('PRE', S['chem'], 6), ('PRE', S['eng'], 4)],
            'Dietetics': [('REQ', S['bio'], 6), ('REQ', S['chem'], 6), ('PRE', S['physics'], 6)],
            'Physiotherapy': [('REQ', S['bio'], 4), ('REQ', S['physics'], 6), ('PRE', S['chem'], 6)],
            'Diagnostic Imaging (Radiography)': [('REQ', S['bio'], 4), ('REQ', S['physics'], 6), ('PRE', S['chem'], 6)],
            'Optometry': [('REQ', S['bio'], 4), ('REQ', S['physics'], 6), ('PRE', S['chem'], 6)],
            'Education (Science)': [('REQ', S['eng'], 6), ('PRE', S['sci'], 6)],
            'Education (Arts)': [('REQ', S['eng'], 6), ('PRE', S['hist'], 6)],
            'Education (Mathematics)': [('REQ', S['emath'], 6), ('REQ', S['eng'], 6)],
            'Education (Early Childhood)': [('REQ', S['eng'], 6)],
            'Fine Arts': [('REQ', S['gkart'], 6), ('PRE', S['eng'], 6)],
            'Communication Design': [('REQ', S['gkart'], 6), ('PRE', S['eng'], 6)],
            'Hospitality Management': [('REQ', S['eng'], 4), ('PRE', S['econ'], 6), ('PRE', S['geo'], 6)],
            'Food Process Engineering': [('REQ', S['emath'], 4), ('REQ', S['physics'], 4), ('PRE', S['chem'], 6)],
            'Renewable Energy Engineering': [('REQ', S['emath'], 4), ('REQ', S['physics'], 4), ('PRE', S['chem'], 6)],
            'Geomatic Engineering': [('REQ', S['emath'], 4), ('REQ', S['physics'], 4), ('PRE', S['geo'], 6)],
            'Earth Science': [('REQ', S['chem'], 6), ('REQ', S['physics'], 6), ('PRE', S['geo'], 6), ('PRE', S['bio'], 6)],
            'Occupational Therapy': [('REQ', S['bio'], 6), ('PRE', S['physics'], 6), ('PRE', S['eng'], 4)],
            'Building Technology': [('REQ', S['emath'], 6), ('PRE', S['physics'], 6), ('PRE', S['td'], 6)],
            'Fashion Design and Textiles': [('REQ', S['eng'], 6), ('PRE', S['gkart'], 6)],
            'Tourism Management': [('REQ', S['eng'], 4), ('PRE', S['geo'], 6), ('PRE', S['econ'], 6)],
            'Building Technology': [('REQ', S['emath'], 6), ('PRE', S['physics'], 6), ('PRE', S['td'], 6)],
            'Fashion Design and Textiles': [('REQ', S['eng'], 6), ('PRE', S['gkart'], 6)],
            'Computer Technology': [('PRE', S['emath'], 6), ('PRE', S['ict'], 6), ('PRE', S['eng'], 6)],
            'Food Technology': [('REQ', S['chem'], 6), ('PRE', S['bio'], 6), ('PRE', S['emath'], 6)],
            'Pharmaceutical Sciences': [('REQ', S['bio'], 6), ('REQ', S['chem'], 6), ('PRE', S['eng'], 4)],
            'Architectural Technology': [('REQ', S['emath'], 6), ('PRE', S['physics'], 6), ('PRE', S['td'], 6)],
            'Interior Design Technology': [('REQ', S['gkart'], 6), ('PRE', S['eng'], 6)],
            'Laboratory Technology': [('REQ', S['chem'], 6), ('PRE', S['bio'], 6), ('PRE', S['physics'], 6)],
            'Dispensing Technology': [('REQ', S['bio'], 6), ('REQ', S['chem'], 6), ('PRE', S['eng'], 4)],
            'Purchasing and Supply': [('REQ', S['eng'], 6), ('PRE', S['econ'], 6)],
            'Estate Management': [('REQ', S['emath'], 6), ('PRE', S['econ'], 6), ('PRE', S['geo'], 6)],
            'Agribusiness': [('REQ', S['eng'], 6), ('PRE', S['econ'], 6), ('PRE', S['emath'], 6)],
            'Entrepreneurship': [('REQ', S['eng'], 6), ('PRE', S['econ'], 6)],
            'Automotive Engineering': [('REQ', S['emath'], 4), ('REQ', S['physics'], 4), ('PRE', S['chem'], 6)],
            'Oil and Gas Engineering': [('REQ', S['emath'], 4), ('REQ', S['physics'], 4), ('REQ', S['chem'], 4)],
            'Mechatronics Engineering': [('REQ', S['emath'], 4), ('REQ', S['physics'], 4), ('PRE', S['chem'], 6)],
            'Procurement and Supply Chain Management': [('REQ', S['eng'], 6), ('PRE', S['econ'], 6), ('PRE', S['emath'], 6)],
        }

        for prog_name, prereqs in prereq_data.items():
            prog = programs.get(prog_name)
            if not prog:
                continue
            for level, subject, min_grade in prereqs:
                ProgramPrerequisite.objects.get_or_create(
                    program=prog,
                    subject=subject,
                    defaults={
                        'requirement_level': level,
                        'min_grade': min_grade,
                    }
                )

        self.stdout.write(f'  Prerequisites set for {len(prereq_data)} programs')

        # ════════════════════════════════════════════
        # PROGRAM DETAILS + ADMISSION TIERS
        # ════════════════════════════════════════════

        # Format: (program_name, institution_name, cutoff_regular, description)
        cutoff_data = [
            # ── University of Ghana ──
            ('Biomedical Engineering', 'University of Ghana', 7, 'Engineering principles applied to medicine and healthcare'),
            ('Computer Engineering', 'University of Ghana', 7, 'Integration of computer science and electrical engineering'),
            ('Computer Science', 'University of Ghana', 9, 'Study of computation, algorithms, and information systems'),
            ('Actuarial Science', 'University of Ghana', 11, 'Mathematical and statistical methods to assess risk'),
            ('Biological Sciences', 'University of Ghana', 15, 'Study of living organisms and life processes'),
            ('Earth Science', 'University of Ghana', 18, 'Study of the Earth and its natural systems'),
            ('Mathematics', 'University of Ghana', 16, 'Advanced mathematical theory and applications'),
            ('Veterinary Medicine', 'University of Ghana', 17, 'Medical care and treatment of animals'),
            ('Agriculture', 'University of Ghana', 22, 'Study of farming, crop production, and land management'),
            ('Medicine and Surgery', 'University of Ghana', 8, 'Medical training leading to the MBChB degree'),
            ('Dental Surgery', 'University of Ghana', 10, 'Oral health and dental surgery'),
            ('Pharmacy', 'University of Ghana', 10, 'Pharmaceutical sciences and drug therapy'),
            ('Nursing', 'University of Ghana', 15, 'Professional nursing practice and healthcare'),
            ('Midwifery', 'University of Ghana', 15, 'Midwifery care for women and newborns'),
            ('Medical Laboratory Science', 'University of Ghana', 12, 'Clinical laboratory diagnostics'),
            ('Physiotherapy', 'University of Ghana', 14, 'Physical therapy and rehabilitation'),
            ('Dietetics', 'University of Ghana', 14, 'Nutrition science and dietary management'),
            ('Diagnostic Imaging (Radiography)', 'University of Ghana', 13, 'Medical imaging techniques and diagnosis'),
            ('Occupational Therapy', 'University of Ghana', 15, 'Therapeutic interventions for daily living'),
            ('Law', 'University of Ghana', 7, 'Legal education leading to the LLB degree'),
            ('Business Administration', 'University of Ghana', 9, 'Management and administrative skills for business'),
            ('Economics', 'University of Ghana', 14, 'Study of resource allocation and economic systems'),
            ('Political Science', 'University of Ghana', 16, 'Study of government, politics, and policy'),
            ('Fine Arts', 'University of Ghana', 22, 'Creative visual arts and artistic expression'),
            ('Psychology', 'University of Ghana', 14, 'Study of mind, behaviour, and mental processes'),
            ('Communication Studies', 'University of Ghana', 14, 'Media, journalism, and strategic communication'),

            # ── KNUST ──
            ('Electrical and Electronic Engineering', 'Kwame Nkrumah University of Science and Technology', 7, 'Electrical systems, power, and electronics'),
            ('Biomedical Engineering', 'Kwame Nkrumah University of Science and Technology', 7, 'Biomedical technology and healthcare engineering'),
            ('Aerospace Engineering', 'Kwame Nkrumah University of Science and Technology', 9, 'Aircraft and spacecraft design and engineering'),
            ('Computer Engineering', 'Kwame Nkrumah University of Science and Technology', 9, 'Hardware and software systems integration'),
            ('Civil Engineering', 'Kwame Nkrumah University of Science and Technology', 10, 'Infrastructure design, construction, and maintenance'),
            ('Mechanical Engineering', 'Kwame Nkrumah University of Science and Technology', 10, 'Machine design, thermodynamics, and manufacturing'),
            ('Chemical Engineering', 'Kwame Nkrumah University of Science and Technology', 10, 'Chemical processes and industrial production'),
            ('Petroleum Engineering', 'Kwame Nkrumah University of Science and Technology', 10, 'Oil and gas exploration and production'),
            ('Marine Engineering', 'Kwame Nkrumah University of Science and Technology', 15, 'Marine vessel design and offshore engineering'),
            ('Agricultural Engineering', 'Kwame Nkrumah University of Science and Technology', 16, 'Engineering applications in agriculture'),
            ('Industrial Engineering', 'Kwame Nkrumah University of Science and Technology', 16, 'Optimization of processes and systems'),
            ('Materials Engineering', 'Kwame Nkrumah University of Science and Technology', 16, 'Properties and applications of materials'),
            ('Medicine and Surgery', 'Kwame Nkrumah University of Science and Technology', 6, 'Medical training leading to the MBChB degree'),
            ('Pharmacy', 'Kwame Nkrumah University of Science and Technology', 12, 'Pharmaceutical sciences and drug therapy'),
            ('Nursing', 'Kwame Nkrumah University of Science and Technology', 16, 'Professional nursing practice and healthcare'),
            ('Midwifery', 'Kwame Nkrumah University of Science and Technology', 16, 'Midwifery care for women and newborns'),
            ('Optometry', 'Kwame Nkrumah University of Science and Technology', 16, 'Vision care and eye health'),
            ('Veterinary Medicine', 'Kwame Nkrumah University of Science and Technology', 16, 'Medical care and treatment of animals'),
            ('Architecture', 'Kwame Nkrumah University of Science and Technology', 18, 'Building design, planning, and construction'),
            ('Construction Technology and Management', 'Kwame Nkrumah University of Science and Technology', 17, 'Construction project management and technology'),
            ('Quantity Surveying and Construction Economics', 'Kwame Nkrumah University of Science and Technology', 17, 'Cost management in construction'),
            ('Land Economy', 'Kwame Nkrumah University of Science and Technology', 17, 'Land management, valuation, and economics'),
            ('Law', 'Kwame Nkrumah University of Science and Technology', 12, 'Legal education leading to the LLB degree'),
            ('Computer Science', 'Kwame Nkrumah University of Science and Technology', 16, 'Study of computation, algorithms, and information systems'),
            ('Actuarial Science', 'Kwame Nkrumah University of Science and Technology', 21, 'Mathematical and statistical methods to assess risk'),
            ('Business Administration', 'Kwame Nkrumah University of Science and Technology', 22, 'Management and administrative skills for business'),

            # ── University of Cape Coast ──
            ('Medicine and Surgery', 'University of Cape Coast', 8, 'Medical training leading to the MBChB degree'),
            ('Biological Sciences', 'University of Cape Coast', 16, 'Study of living organisms and life processes'),
            ('Diagnostic Imaging (Radiography)', 'University of Cape Coast', 14, 'Medical imaging techniques and diagnosis'),
            ('Dietetics', 'University of Cape Coast', 14, 'Nutrition science and dietary management'),
            ('Law', 'University of Cape Coast', 12, 'Legal education leading to the LLB degree'),
            ('Accounting', 'University of Cape Coast', 15, 'Financial accounting and reporting'),
            ('Finance', 'University of Cape Coast', 16, 'Financial management and analysis'),
            ('Human Resource Management', 'University of Cape Coast', 17, 'Personnel management and organizational behaviour'),
            ('Computer Science', 'University of Cape Coast', 15, 'Study of computation, algorithms, and information systems'),
            ('Communication Studies', 'University of Cape Coast', 17, 'Media, journalism, and strategic communication'),
            ('Education (Science)', 'University of Cape Coast', 22, 'Teacher training in science education'),
            ('Education (Mathematics)', 'University of Cape Coast', 18, 'Teacher training in mathematics education'),
            ('Education (Arts)', 'University of Cape Coast', 16, 'Teacher training in arts education'),
            ('Education (Early Childhood)', 'University of Cape Coast', 20, 'Early childhood education and development'),

            # ── UDS ──
            ('Medicine and Surgery', 'University for Development Studies', 8, 'Medical training leading to the MBChB degree'),
            ('Pharmacy', 'University for Development Studies', 10, 'Pharmaceutical sciences and drug therapy'),
            ('Nursing', 'University for Development Studies', 16, 'Professional nursing practice and healthcare'),
            ('Midwifery', 'University for Development Studies', 16, 'Midwifery care for women and newborns'),
            ('Medical Laboratory Science', 'University for Development Studies', 12, 'Clinical laboratory diagnostics'),
            ('Computer Science', 'University for Development Studies', 16, 'Study of computation, algorithms, and information systems'),
            ('Accounting', 'University for Development Studies', 20, 'Financial accounting and reporting'),
            ('Agriculture', 'University for Development Studies', 22, 'Study of farming, crop production, and land management'),
            ('Renewable Energy Engineering', 'University for Development Studies', 16, 'Sustainable energy technologies'),
            ('Law', 'University for Development Studies', 10, 'Legal education leading to the LLB degree'),

            # ── UHAS ──
            ('Medicine and Surgery', 'University of Health and Allied Sciences', 8, 'Medical training leading to the MBChB degree'),
            ('Dental Surgery', 'University of Health and Allied Sciences', 8, 'Oral health and dental surgery'),
            ('Pharmacy', 'University of Health and Allied Sciences', 8, 'Pharmaceutical sciences and drug therapy'),
            ('Medical Laboratory Science', 'University of Health and Allied Sciences', 10, 'Clinical laboratory diagnostics'),
            ('Diagnostic Imaging (Radiography)', 'University of Health and Allied Sciences', 12, 'Medical imaging techniques and diagnosis'),
            ('Dietetics', 'University of Health and Allied Sciences', 14, 'Nutrition science and dietary management'),
            ('Nursing', 'University of Health and Allied Sciences', 15, 'Professional nursing practice and healthcare'),
            ('Midwifery', 'University of Health and Allied Sciences', 15, 'Midwifery care for women and newborns'),
            ('Physiotherapy', 'University of Health and Allied Sciences', 16, 'Physical therapy and rehabilitation'),
            ('Public Health', 'University of Health and Allied Sciences', 19, 'Population health and disease prevention'),

            # ── UPSA ──
            ('Law', 'University of Professional Studies, Accra', 10, 'Legal education with business and corporate focus'),
            ('Actuarial Science', 'University of Professional Studies, Accra', 12, 'Mathematical and statistical methods to assess risk'),
            ('Accounting', 'University of Professional Studies, Accra', 14, 'Financial accounting and reporting'),
            ('Banking and Finance', 'University of Professional Studies, Accra', 20, 'Banking operations and financial management'),
            ('Data Science', 'University of Professional Studies, Accra', 14, 'Data analytics and computational methods'),
            ('Cyber Security', 'University of Professional Studies, Accra', 14, 'Information security and network protection'),
            ('Software Engineering', 'University of Professional Studies, Accra', 14, 'Software development and engineering'),
            ('Human Resource Management', 'University of Professional Studies, Accra', 18, 'Personnel management and organizational behaviour'),
            ('Marketing', 'University of Professional Studies, Accra', 18, 'Marketing strategy and brand management'),
            ('Public Relations Management', 'University of Professional Studies, Accra', 20, 'Corporate communication and public affairs'),
            ('Business Administration', 'University of Professional Studies, Accra', 14, 'Management and administrative skills for business'),

            # ── UMaT ──
            ('Mining Engineering', 'University of Mines and Technology', 10, 'Mining operations and mineral extraction'),
            ('Petroleum Engineering', 'University of Mines and Technology', 10, 'Oil and gas exploration and production'),
            ('Geomatic Engineering', 'University of Mines and Technology', 12, 'Geospatial data and surveying'),
            ('Mechanical Engineering', 'University of Mines and Technology', 12, 'Machine design and industrial mechanics'),
            ('Electrical and Electronic Engineering', 'University of Mines and Technology', 12, 'Electrical power and electronic systems'),
            ('Environmental Science', 'University of Mines and Technology', 15, 'Environmental monitoring and management'),
            ('Computer Science', 'University of Mines and Technology', 16, 'Study of computation, algorithms, and information systems'),

            # ── Accra Technical University ──
            ('Civil Engineering', 'Accra Technical University', 24, 'Infrastructure design and construction'),
            ('Mechanical Engineering', 'Accra Technical University', 24, 'Machine design and manufacturing'),
            ('Electrical and Electronic Engineering', 'Accra Technical University', 24, 'Electrical power and electronics'),
            ('Computer Science', 'Accra Technical University', 24, 'Study of computation and information systems'),
            ('Computer Technology', 'Accra Technical University', 24, 'Computer hardware and systems technology'),
            ('Information Technology', 'Accra Technical University', 24, 'IT infrastructure and support'),
            ('Cyber Security', 'Accra Technical University', 24, 'Information security and network protection'),
            ('Medical Laboratory Science', 'Accra Technical University', 24, 'Clinical laboratory diagnostics'),
            ('Pharmaceutical Sciences', 'Accra Technical University', 24, 'Pharmaceutical technology'),
            ('Accounting', 'Accra Technical University', 24, 'Financial accounting and reporting'),
            ('Business Administration', 'Accra Technical University', 24, 'General business management'),
            ('Marketing', 'Accra Technical University', 24, 'Marketing and brand management'),
            ('Procurement and Supply Chain Management', 'Accra Technical University', 24, 'Supply chain and logistics'),
            ('Fashion Design and Textiles', 'Accra Technical University', 24, 'Textile and fashion production'),
            ('Hospitality Management', 'Accra Technical University', 24, 'Hotel and tourism management'),

            # ── Takoradi Technical University ──
            ('Computer Science', 'Takoradi Technical University', 14, 'Study of computation and information systems'),
            ('Information Technology', 'Takoradi Technical University', 18, 'IT infrastructure and support'),
            ('Civil Engineering', 'Takoradi Technical University', 18, 'Infrastructure design and construction'),
            ('Mechanical Engineering', 'Takoradi Technical University', 18, 'Machine design and manufacturing'),
            ('Electrical and Electronic Engineering', 'Takoradi Technical University', 18, 'Electrical power and electronics'),
            ('Building Technology', 'Takoradi Technical University', 18, 'Construction and building technology'),
            ('Accounting', 'Takoradi Technical University', 18, 'Financial accounting and reporting'),
            ('Business Administration', 'Takoradi Technical University', 18, 'General business management'),
            ('Hospitality Management', 'Takoradi Technical University', 18, 'Hotel and tourism management'),
            ('Fashion Design and Textiles', 'Takoradi Technical University', 18, 'Textile and fashion production'),
            ('Purchasing and Supply', 'Takoradi Technical University', 18, 'Procurement and supply chain'),

            # ── Ashesi University ──
            ('Computer Science', 'Ashesi University', 18, 'Computer science with a focus on ethics and leadership'),
            ('Computer Engineering', 'Ashesi University', 18, 'Engineering with a liberal arts foundation'),
            ('Business Administration', 'Ashesi University', 18, 'Business with ethical leadership focus'),

            # ── Valley View University ──
            ('Business Administration', 'Valley View University', 30, 'General business management'),
            ('Accounting', 'Valley View University', 30, 'Financial accounting and reporting'),
            ('Computer Science', 'Valley View University', 30, 'Study of computation, algorithms, and information systems'),

            # ── Central University ──
            ('Business Administration', 'Central University', 28, 'General business management'),
            ('Accounting', 'Central University', 28, 'Financial accounting and reporting'),
            ('Computer Science', 'Central University', 28, 'Study of computation, algorithms, and information systems'),
            ('Law', 'Central University', 20, 'Legal education leading to the LLB degree'),

            # ── Kumasi Technical University ──
            ('Civil Engineering', 'Kumasi Technical University', 24, 'Infrastructure design and construction'),
            ('Mechanical Engineering', 'Kumasi Technical University', 24, 'Machine design and manufacturing'),
            ('Electrical and Electronic Engineering', 'Kumasi Technical University', 24, 'Electrical power and electronics'),
            ('Automotive Engineering', 'Kumasi Technical University', 24, 'Automotive design and maintenance engineering'),
            ('Chemical Engineering', 'Kumasi Technical University', 24, 'Chemical processes and industrial production'),
            ('Oil and Gas Engineering', 'Kumasi Technical University', 24, 'Petroleum and gas engineering technology'),
            ('Mechatronics Engineering', 'Kumasi Technical University', 24, 'Integration of mechanical and electronic systems'),
            ('Computer Science', 'Kumasi Technical University', 24, 'Study of computation and information systems'),
            ('Computer Technology', 'Kumasi Technical University', 24, 'Computer hardware and systems technology'),
            ('Data Science', 'Kumasi Technical University', 24, 'Data analytics and computational methods'),
            ('Accounting', 'Kumasi Technical University', 24, 'Financial accounting and reporting'),
            ('Business Administration', 'Kumasi Technical University', 24, 'General business management'),
            ('Banking and Finance', 'Kumasi Technical University', 24, 'Banking operations and financial management'),
            ('Procurement and Supply Chain Management', 'Kumasi Technical University', 24, 'Supply chain and logistics'),
            ('Hospitality Management', 'Kumasi Technical University', 28, 'Hotel and tourism management'),
            ('Fashion Design and Textiles', 'Kumasi Technical University', 28, 'Textile and fashion production'),
            ('Building Technology', 'Kumasi Technical University', 24, 'Construction and building technology'),
            ('Architectural Technology', 'Kumasi Technical University', 24, 'Building design and architectural technology'),
            ('Quantity Surveying and Construction Economics', 'Kumasi Technical University', 24, 'Construction cost management'),
            ('Interior Design Technology', 'Kumasi Technical University', 28, 'Interior space design and decoration'),
            ('Food Technology', 'Kumasi Technical University', 24, 'Food processing and preservation technology'),
            ('Pharmaceutical Sciences', 'Kumasi Technical University', 24, 'Pharmaceutical technology and dispensing'),
            ('Medical Laboratory Science', 'Kumasi Technical University', 24, 'Clinical laboratory diagnostics'),
            ('Laboratory Technology', 'Kumasi Technical University', 24, 'Industrial and science laboratory technology'),
            ('Estate Management', 'Kumasi Technical University', 24, 'Property management and valuation'),
            ('Agribusiness', 'Kumasi Technical University', 24, 'Agricultural business and entrepreneurship'),

            # ── Cape Coast Technical University ──
            ('Civil Engineering', 'Cape Coast Technical University', 24, 'Infrastructure design and construction'),
            ('Mechanical Engineering', 'Cape Coast Technical University', 24, 'Machine design and manufacturing'),
            ('Electrical and Electronic Engineering', 'Cape Coast Technical University', 24, 'Electrical power and electronics'),
            ('Building Technology', 'Cape Coast Technical University', 24, 'Construction and building technology'),
            ('Computer Science', 'Cape Coast Technical University', 28, 'Study of computation and information systems'),
            ('Information Technology', 'Cape Coast Technical University', 28, 'IT infrastructure and support'),
            ('Business Administration', 'Cape Coast Technical University', 28, 'General business management'),
            ('Accounting', 'Cape Coast Technical University', 28, 'Financial accounting and reporting'),
            ('Hospitality Management', 'Cape Coast Technical University', 28, 'Hotel and tourism management'),
            ('Tourism Management', 'Cape Coast Technical University', 28, 'Travel and tourism operations'),
            ('Marketing', 'Cape Coast Technical University', 28, 'Marketing and brand management'),
            ('Agribusiness', 'Cape Coast Technical University', 28, 'Agricultural business and entrepreneurship'),

            # ── Koforidua Technical University ──
            ('Computer Science', 'Koforidua Technical University', 24, 'Study of computation and information systems'),
            ('Information Technology', 'Koforidua Technical University', 24, 'IT infrastructure and support'),
            ('Computer Technology', 'Koforidua Technical University', 24, 'Computer hardware and systems technology'),
            ('Accounting', 'Koforidua Technical University', 24, 'Financial accounting and reporting'),
            ('Business Administration', 'Koforidua Technical University', 24, 'General business management'),
            ('Human Resource Management', 'Koforidua Technical University', 24, 'Personnel and HR management'),
            ('Marketing', 'Koforidua Technical University', 24, 'Marketing and brand management'),
            ('Procurement and Supply Chain Management', 'Koforidua Technical University', 24, 'Supply chain and logistics'),
            ('Electrical and Electronic Engineering', 'Koforidua Technical University', 24, 'Electrical power and electronics'),
            ('Mechanical Engineering', 'Koforidua Technical University', 24, 'Machine design and manufacturing'),
            ('Civil Engineering', 'Koforidua Technical University', 24, 'Infrastructure design and construction'),
            ('Nursing', 'Koforidua Technical University', 24, 'Professional nursing practice'),
            ('Medical Laboratory Science', 'Koforidua Technical University', 24, 'Clinical laboratory diagnostics'),
            ('Pharmaceutical Sciences', 'Koforidua Technical University', 24, 'Pharmaceutical technology'),
            ('Statistics', 'Koforidua Technical University', 24, 'Statistical methods and data analysis'),

            # ── Ho Technical University ──
            ('Computer Science', 'Ho Technical University', 24, 'Study of computation and information systems'),
            ('Information Technology', 'Ho Technical University', 24, 'IT infrastructure and support'),
            ('Accounting', 'Ho Technical University', 24, 'Financial accounting and reporting'),
            ('Business Administration', 'Ho Technical University', 24, 'General business management'),
            ('Hospitality Management', 'Ho Technical University', 24, 'Hotel and tourism management'),
            ('Tourism Management', 'Ho Technical University', 24, 'Travel and tourism operations'),
            ('Marketing', 'Ho Technical University', 24, 'Marketing and brand management'),
            ('Human Resource Management', 'Ho Technical University', 24, 'Personnel and HR management'),
            ('Electrical and Electronic Engineering', 'Ho Technical University', 24, 'Electrical power and electronics'),
            ('Civil Engineering', 'Ho Technical University', 24, 'Infrastructure design and construction'),
            ('Mechanical Engineering', 'Ho Technical University', 24, 'Machine design and manufacturing'),
            ('Building Technology', 'Ho Technical University', 24, 'Construction and building technology'),
            ('Nursing', 'Ho Technical University', 24, 'Professional nursing practice'),
            ('Dietetics', 'Ho Technical University', 24, 'Nutrition science and dietary management'),
            ('Pharmaceutical Sciences', 'Ho Technical University', 24, 'Pharmaceutical technology'),

            # ── Tamale Technical University ──
            ('Computer Science', 'Tamale Technical University', 24, 'Study of computation and information systems'),
            ('Information Technology', 'Tamale Technical University', 24, 'IT infrastructure and support'),
            ('Accounting', 'Tamale Technical University', 24, 'Financial accounting and reporting'),
            ('Business Administration', 'Tamale Technical University', 24, 'General business management'),
            ('Banking and Finance', 'Tamale Technical University', 24, 'Banking operations and financial management'),
            ('Agricultural Engineering', 'Tamale Technical University', 24, 'Engineering for agricultural applications'),
            ('Civil Engineering', 'Tamale Technical University', 24, 'Infrastructure design and construction'),
            ('Electrical and Electronic Engineering', 'Tamale Technical University', 24, 'Electrical power and electronics'),
            ('Mechanical Engineering', 'Tamale Technical University', 24, 'Machine design and manufacturing'),
            ('Building Technology', 'Tamale Technical University', 24, 'Construction and building technology'),
            ('Nursing', 'Tamale Technical University', 24, 'Professional nursing practice'),
            ('Agriculture', 'Tamale Technical University', 24, 'Crop production and farm management'),
            ('Agribusiness', 'Tamale Technical University', 24, 'Agricultural business and entrepreneurship'),
            ('Hospitality Management', 'Tamale Technical University', 24, 'Hotel and tourism management'),

            # ── Sunyani Technical University ──
            ('Computer Science', 'Sunyani Technical University', 24, 'Study of computation and information systems'),
            ('Information Technology', 'Sunyani Technical University', 24, 'IT infrastructure and support'),
            ('Computer Technology', 'Sunyani Technical University', 24, 'Computer hardware and systems technology'),
            ('Accounting', 'Sunyani Technical University', 24, 'Financial accounting and reporting'),
            ('Business Administration', 'Sunyani Technical University', 24, 'General business management'),
            ('Banking and Finance', 'Sunyani Technical University', 24, 'Banking operations and financial management'),
            ('Procurement and Supply Chain Management', 'Sunyani Technical University', 24, 'Supply chain and logistics'),
            ('Electrical and Electronic Engineering', 'Sunyani Technical University', 24, 'Electrical power and electronics'),
            ('Mechanical Engineering', 'Sunyani Technical University', 24, 'Machine design and manufacturing'),
            ('Civil Engineering', 'Sunyani Technical University', 24, 'Infrastructure design and construction'),
            ('Agricultural Engineering', 'Sunyani Technical University', 24, 'Engineering for agricultural applications'),
            ('Building Technology', 'Sunyani Technical University', 24, 'Construction and building technology'),
            ('Hospitality Management', 'Sunyani Technical University', 24, 'Hotel and tourism management'),
            ('Tourism Management', 'Sunyani Technical University', 24, 'Travel and tourism operations'),
            ('Nursing', 'Sunyani Technical University', 24, 'Professional nursing practice'),
            ('Renewable Energy Engineering', 'Sunyani Technical University', 24, 'Sustainable energy technologies'),
            ('Agriculture', 'Sunyani Technical University', 24, 'Crop production and farm management'),
            ('Agribusiness', 'Sunyani Technical University', 24, 'Agricultural business and entrepreneurship'),

            # ── Bolgatanga Technical University ──
            ('Computer Science', 'Bolgatanga Technical University', 28, 'Study of computation and information systems'),
            ('Information Technology', 'Bolgatanga Technical University', 28, 'IT infrastructure and support'),
            ('Accounting', 'Bolgatanga Technical University', 28, 'Financial accounting and reporting'),
            ('Business Administration', 'Bolgatanga Technical University', 28, 'General business management'),
            ('Human Resource Management', 'Bolgatanga Technical University', 28, 'Personnel and HR management'),
            ('Civil Engineering', 'Bolgatanga Technical University', 28, 'Infrastructure design and construction'),
            ('Electrical and Electronic Engineering', 'Bolgatanga Technical University', 28, 'Electrical power and electronics'),
            ('Mechanical Engineering', 'Bolgatanga Technical University', 28, 'Machine design and manufacturing'),
            ('Building Technology', 'Bolgatanga Technical University', 28, 'Construction and building technology'),
            ('Hospitality Management', 'Bolgatanga Technical University', 28, 'Hotel and tourism management'),
            ('Agriculture', 'Bolgatanga Technical University', 28, 'Crop production and farm management'),
            ('Agribusiness', 'Bolgatanga Technical University', 28, 'Agricultural business and entrepreneurship'),

            # ── Wa Technical University ──
            ('Computer Science', 'Wa Technical University', 28, 'Study of computation and information systems'),
            ('Information Technology', 'Wa Technical University', 28, 'IT infrastructure and support'),
            ('Accounting', 'Wa Technical University', 28, 'Financial accounting and reporting'),
            ('Business Administration', 'Wa Technical University', 28, 'General business management'),
            ('Human Resource Management', 'Wa Technical University', 28, 'Personnel and HR management'),
            ('Civil Engineering', 'Wa Technical University', 28, 'Infrastructure design and construction'),
            ('Electrical and Electronic Engineering', 'Wa Technical University', 28, 'Electrical power and electronics'),
            ('Mechanical Engineering', 'Wa Technical University', 28, 'Machine design and manufacturing'),
            ('Building Technology', 'Wa Technical University', 28, 'Construction and building technology'),
            ('Hospitality Management', 'Wa Technical University', 28, 'Hotel and tourism management'),
            ('Agriculture', 'Wa Technical University', 28, 'Crop production and farm management'),
            ('Agribusiness', 'Wa Technical University', 28, 'Agricultural business and entrepreneurship'),

            # ── Lancaster University Ghana ──
            ('Computer Science', 'Lancaster University Ghana', 24, 'Computer science with UK curriculum'),
            ('Business Administration', 'Lancaster University Ghana', 24, 'Management with UK curriculum'),
            ('Accounting', 'Lancaster University Ghana', 24, 'Accounting and finance with UK curriculum'),
            ('Law', 'Lancaster University Ghana', 20, 'LLB with UK curriculum'),
        ]

        tier_count = 0
        pd_count_existing = ProgramDetails.objects.count()

        for prog_name, inst_name, cutoff, desc in cutoff_data:
            prog = programs.get(prog_name)
            inst = institutions.get(inst_name)
            if not prog or not inst:
                self.stdout.write(f'  SKIP: {prog_name} @ {inst_name} — missing program or institution')
                continue

            pd, created = ProgramDetails.objects.get_or_create(
                program=prog,
                institution=inst,
                defaults={
                    'cutoff_point': cutoff,
                    'description': desc,
                    'is_active': True,
                }
            )

            if created:
                pd_count_existing += 1

            # Always ensure a tier exists
            _, tier_created = ProgramAdmissionTier.objects.get_or_create(
                program_details=pd,
                tier_name='Regular',
                defaults={
                    'cutoff_aggregate': cutoff,
                    'gender': 'ANY',
                }
            )
            if tier_created:
                tier_count += 1

        self.stdout.write(f'  {pd_count_existing} program details')
        self.stdout.write(f'  {tier_count} admission tiers created')

        # ── Clean up duplicate ProgramDetails ──
        from django.db.models import Count
        dupes = ProgramDetails.objects.values('program', 'institution').annotate(
            cnt=Count('id')).filter(cnt__gt=1)
        for dupe in dupes:
            pds = ProgramDetails.objects.filter(
                program=dupe['program'], institution=dupe['institution'])
            keep = pds.first()
            for pd in pds[1:]:
                pd.delete()
                self.stdout.write(f'  Removed duplicate: {pd}')

        self.stdout.write(self.style.SUCCESS(f'Done! Seeded {len(cutoff_data)} programme-institution entries.'))
