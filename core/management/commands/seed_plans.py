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
        'name': 'Freemium',
        'slug': 'freemium',
        'description': 'More insights for serious explorers.',
        'price_monthly': 15,
        'price_yearly': 150,
        'sort_order': 1,
        'badge_label': 'Popular',
        'color': '#2d5a8e',
        'features': ['find_my_path', 'find_schools', 'career_basic', 'career_detailed', 'past_questions_limited'],
    },
    {
        'name': 'Premium Basic',
        'slug': 'premium-basic',
        'description': 'Full access for committed students.',
        'price_monthly': 40,
        'price_yearly': 400,
        'sort_order': 2,
        'badge_label': '',
        'color': '#1e3a5f',
        'features': ['find_my_path', 'find_schools', 'career_basic', 'career_detailed', 'past_questions'],
    },
    {
        'name': 'Premium Pro',
        'slug': 'premium-pro',
        'description': 'Everything including priority support.',
        'price_monthly': 70,
        'price_yearly': 700,
        'sort_order': 3,
        'badge_label': 'Best Value',
        'color': '#c2410c',
        'features': ['find_my_path', 'find_schools', 'career_basic', 'career_detailed', 'past_questions', 'detailed_analytics', 'priority_support'],
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

        self.stdout.write(self.style.SUCCESS('Done seeding subscription data'))
