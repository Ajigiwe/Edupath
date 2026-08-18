# core/urls.py
from django.urls import path
from core.views.home_view import findmypath, alreadyknow, careeroutcome, stream_subjects_api, page_view
from core.views.auth_view import login_view, logout_view, signup_view, request_otp
from core.views.institutions_list_view import institutions_list

from core.views.pastquestion_view import past_questions
from core.views.pastquestion_view import create_theory, add_theory_page
from core.views.pastquestion_view import create_mcq, add_mcq_page
from core.views.pastquestion_view import upload_questions_page, sample_questions_json
from core.views.practice_view import practice_home, practice_start, practice_quiz, practice_result
# from core.views.pastquestion_view import pastquestion
from core.views.department_view import *
from core.views.course_view import *
from core.views.schoollevel_view import *
from core.views.program_view import *
from core.views.institution_view import *
from core.views.ownership_view import *
from core.views.institutiontype_view import *
from core.views.level_view import *
from core.views.program_details_view import *
from core.views.interest_view import *
from core.views.profile_view import profile_view, update_profile, change_password
from core.views.subscription_view import plans_view, my_subscription, subscribe, paystack_callback
from core.views.terminal_view import terminal_home, terminal_upload, terminal_result
from core.views.settings_view import site_settings_view, download_backup, restore_backup, clear_data
from core.views.admin_dashboard_view import admin_dashboard
from core.views.plan_view import plan_dashboard, create_plan, update_plan, delete_plan
from core.views.user_view import user_dashboard, update_user, manage_subscription
from core.views.transaction_view import transaction_dashboard, record_transaction, update_transaction_status

urlpatterns = [
    # ================= Admin Dashboard =================
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),

    # ================= findmypath =================
    path('findmypath/', findmypath, name='findmypath'),
    path('alreadyknow/', alreadyknow, name='alreadyknow'),
    path('careeroutcome/', careeroutcome, name='careeroutcome'),
    path('api/stream-subjects/<slug:stream_slug>/', stream_subjects_api, name='stream_subjects_api'),

    path('institutions_list/', institutions_list, name='institutions'),
    path('past-questions/<uuid:id>/', past_questions, name='past_questions'),
    path('practice/', practice_home, name='practice_home'),
    path('practice/start/', practice_start, name='practice_start'),
    path('practice/quiz/<uuid:session_id>/', practice_quiz, name='practice_quiz'),
    path('practice/result/<uuid:session_id>/', practice_result, name='practice_result'),
    # ADD
    #path('add-theory/', create_theory, name='create_theory'),
    #path('add-mcq/', create_mcq, name='create_mcq'),
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('request-otp/', request_otp, name='request_otp'),
    path('logout/', logout_view, name='logout'),

     # 👉 NEW PAGES
    path('add-theory-page/', add_theory_page, name='add_theory_page'),
    path('add-mcq-page/', add_mcq_page, name='add_mcq_page'),

    # 👉 FORM SUBMIT
    path('add-theory/', create_theory, name='create_theory'),
    path('add-mcq/', create_mcq, name='create_mcq'),

    # 👉 BULK UPLOAD
    path('upload-questions/', upload_questions_page, name='upload_questions_page'),
    path('sample-questions.json', sample_questions_json, name='sample_questions_json'),


    path('departments/', department_dashboard, name='department_dashboard'),
    path('departments/create/', create_department, name='create_department'),
    path('departments/update/<uuid:department_id>/', update_department, name='update_department'),
    path('departments/delete/<uuid:department_id>/', delete_department, name='delete_department'),

    # path('courses/', course_dashboard, name='course_dashboard'),
    # path('school-levels/', schoollevel_dashboard, name='schoollevel_dashboard'),

    # COURSE
    path('courses/', course_dashboard, name='course_dashboard'),
    path('courses/create/', create_course, name='create_course'),
    path('courses/update/<uuid:course_id>/', update_course, name='update_course'),
    path('courses/delete/<uuid:course_id>/', delete_course, name='delete_course'),

    # SCHOOL LEVEL
    path('school-levels/', schoollevel_dashboard, name='schoollevel_dashboard'),
    path('school-levels/create/', create_schoollevel, name='create_schoollevel'),
    path('school-levels/update/<uuid:level_id>/', update_schoollevel, name='update_schoollevel'),
    path('school-levels/delete/<uuid:level_id>/', delete_schoollevel, name='delete_schoollevel'),

    # ================= INTERESTS =================
    path('interests/', interest_dashboard, name='interest_dashboard'),
    path('interests/create/', create_interest, name='create_interest'),
    path('interests/update/<uuid:interest_id>/', update_interest, name='update_interest'),
    path('interests/delete/<uuid:interest_id>/', delete_interest, name='delete_interest'),

    # ================= PROGRAM =================
    path('programs/', program_dashboard, name='program_dashboard'),
    path('programs/create/', create_program, name='create_program'),
    path('programs/update/<uuid:program_id>/', update_program, name='update_program'),
    path('programs/delete/<uuid:program_id>/', delete_program, name='delete_program'),

    # ================= INSTITUTION =================
    path('institutions/', institution_dashboard, name='institution_dashboard'),
    path('institutions/create/', create_institution, name='create_institution'),
    path('institutions/update/<uuid:institution_id>/', update_institution, name='update_institution'),
    path('institutions/delete/<uuid:institution_id>/', delete_institution, name='delete_institution'),

     # ================= Ownerships =================
    path('ownerships/', ownership_dashboard, name='ownership_dashboard'),
    path('ownerships/create/', create_ownership, name='create_ownership'),
    path('ownerships/update/<uuid:ownership_id>/', update_ownership, name='update_ownership'),
    path('ownerships/delete/<uuid:ownership_id>/', delete_ownership, name='delete_ownership'),

    # ================= Institution Types =================
    path('institution-types/', institutiontype_dashboard, name='institutiontype_dashboard'),
    path('institution-types/create/', create_institutiontype, name='create_institutiontype'),
    path('institution-types/update/<uuid:type_id>/', update_institutiontype, name='update_institutiontype'),
    path('institution-types/delete/<uuid:type_id>/', delete_institutiontype, name='delete_institutiontype'),

    # ================= Levels =================
    path('levels/', level_dashboard, name='level_dashboard'),
    path('levels/create/', create_level, name='create_level'),
    path('levels/update/<uuid:level_id>/', update_level, name='update_level'),
    path('levels/delete/<uuid:level_id>/', delete_level, name='delete_level'),

    # ================= Program Details =================
    path('program-details/', program_details_dashboard, name='program_details_dashboard'),
    path('program-details/create/', create_program_detail, name='create_program_detail'),
    path('program-details/update/<uuid:detail_id>/', update_program_detail, name='update_program_detail'),
    path('program-details/delete/<uuid:detail_id>/', delete_program_detail, name='delete_program_detail'),

    # ================= Profile =================
    path('profile/', profile_view, name='profile'),
    path('profile/update/', update_profile, name='update_profile'),
    path('profile/change-password/', change_password, name='change_password'),

    # ================= Subscription / Plans =================
    path('plans/', plans_view, name='plans'),
    path('plan-admin/', plan_dashboard, name='plan_dashboard'),
    path('plan-admin/create/', create_plan, name='create_plan'),
    path('plan-admin/update/<uuid:plan_id>/', update_plan, name='update_plan'),
    path('plan-admin/delete/<uuid:plan_id>/', delete_plan, name='delete_plan'),
    path('my-subscription/', my_subscription, name='my_subscription'),
    path('subscribe/<slug:plan_slug>/', subscribe, name='subscribe'),
    path('paystack/callback/', paystack_callback, name='paystack_callback'),

    # ================= Terminal Analysis =================
    path('terminal/', terminal_home, name='terminal_home'),
    path('terminal/upload/', terminal_upload, name='terminal_upload'),
    path('terminal/result/<uuid:report_id>/', terminal_result, name='terminal_result'),

    # ================= Users =================
    path('users/', user_dashboard, name='user_dashboard'),
    path('users/update/<int:user_id>/', update_user, name='update_user'),
    path('users/subscription/<int:user_id>/', manage_subscription, name='manage_subscription'),

    # ================= Transactions =================
    path('transactions/', transaction_dashboard, name='transaction_dashboard'),
    path('transactions/record/', record_transaction, name='record_transaction'),
    path('transactions/update/<uuid:payment_id>/', update_transaction_status, name='update_transaction_status'),

    # ================= Admin Settings =================
    path('settings/', site_settings_view, name='site_settings'),
    path('settings/backup/', download_backup, name='download_backup'),
    path('settings/restore/', restore_backup, name='restore_backup'),
    path('settings/clear/', clear_data, name='clear_data'),

    # ================= Static Pages =================
    path('about/', page_view, {'slug': 'about'}, name='about'),
    path('contact/', page_view, {'slug': 'contact'}, name='contact'),
    path('how-it-works/', page_view, {'slug': 'how-it-works'}, name='how_it_works'),
    path('privacy/', page_view, {'slug': 'privacy'}, name='privacy'),
    path('faq/', page_view, {'slug': 'faq'}, name='faq'),
    path('terms/', page_view, {'slug': 'terms'}, name='terms'),
]
