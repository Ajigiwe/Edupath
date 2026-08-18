from django.core.management.base import BaseCommand
from core.models import PlanFeature, SubscriptionPlan, PlanFeatureThrough


FEATURES = [
    ('Find My Path', 'find_my_path', 'find_my_path', 'Guided programme matching wizard'),
    ('Find Schools', 'find_schools', 'find_schools', 'Browse institutions offering programmes'),
    ('Career Outcomes (Basic)', 'career_basic', 'career_basic', 'Basic career outcome summaries'),
    ('Career Outcomes (Detailed)', 'career_detailed', 'career_detailed', 'Detailed career insights, job scores, competitiveness'),
    ('Past Questions (5/mo)', 'past_questions_limited', 'past_questions_limited', 'Access to 5 past question papers per month'),
    ('Past Questions (Unlimited)', 'past_questions', 'past_questions', 'Unlimited access to all past question papers'),
    ('Detailed Analytics', 'detailed_analytics', 'detailed_analytics', 'Advanced programme comparison and fit analytics'),
    ('Priority Support', 'priority_support', 'priority_support', 'Email and chat priority support'),
    ('Termly Progress Analysis', 'terminal_analysis', 'terminal_analysis', 'Upload term results and track progress towards your path'),
]

PLANS = [
    {
        'name': 'Free',
        'slug': 'free',
        'description': 'Get started with basic career guidance at no cost.',
        'price_monthly': 0,
        'price_yearly': 0,
        'sort_order': 0,
        'badge_label': '',
        'color': '#78716c',
        'features': ['find_my_path', 'find_schools', 'career_basic'],
    },
    {
        'name': 'Premium',
        'slug': 'premium',
        'description': 'Everything unlocked. All paid features plus unlimited access.',
        'price_monthly': 40,
        'price_yearly': 400,
        'sort_order': 1,
        'badge_label': 'Best Value',
        'color': '#1e3a5f',
        'features': [
            'find_my_path', 'find_schools', 'career_basic', 'career_detailed',
            'past_questions', 'detailed_analytics', 'priority_support', 'terminal_analysis',
        ],
    },
]


class Command(BaseCommand):
    help = 'Seed default subscription plans and features'

    def handle(self, *args, **options):
        # Create features
        created_features = {}
        for name, slug, codename, desc in FEATURES:
            feat, was_created = PlanFeature.objects.get_or_create(
                codename=codename,
                defaults={'name': name, 'slug': slug, 'description': desc}
            )
            created_features[codename] = feat
            if was_created:
                self.stdout.write(f'  Created feature: {name}')

        # Create plans
        desired_slugs = [p['slug'] for p in PLANS]
        for plan_data in PLANS:
            plan, was_created = SubscriptionPlan.objects.get_or_create(
                slug=plan_data['slug'],
                defaults={
                    'name': plan_data['name'],
                    'description': plan_data['description'],
                    'price_monthly': plan_data['price_monthly'],
                    'price_yearly': plan_data['price_yearly'],
                    'sort_order': plan_data['sort_order'],
                    'badge_label': plan_data['badge_label'],
                    'color': plan_data['color'],
                }
            )
            plan.is_active = True
            plan.save()
            if not was_created and plan.color != plan_data['color']:
                plan.color = plan_data['color']
                plan.save()
            if was_created:
                self.stdout.write(f'  Created plan: {plan_data["name"]}')

            # Set features
            current = set(plan.planfeaturethrough_set.values_list('feature__codename', flat=True))
            desired = set(plan_data['features'])
            for codename in desired - current:
                PlanFeatureThrough.objects.get_or_create(plan=plan, feature=created_features[codename])
                self.stdout.write(f'    Added {codename} to {plan_data["name"]}')
            for codename in current - desired:
                PlanFeatureThrough.objects.filter(plan=plan, feature__codename=codename).delete()
                self.stdout.write(f'    Removed {codename} from {plan_data["name"]}')

        # Deactivate any plans no longer in the desired list (legacy plans).
        for legacy in SubscriptionPlan.objects.exclude(slug__in=desired_slugs):
            if legacy.is_active:
                legacy.is_active = False
                legacy.save()
                self.stdout.write(f'  Deactivated legacy plan: {legacy.name}')

        self.stdout.write(self.style.SUCCESS('Done seeding subscription data'))
