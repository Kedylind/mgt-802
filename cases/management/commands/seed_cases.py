"""
Management command to seed 10 pre-defined cases (5 consulting, 5 product management).

Usage:
    python manage.py seed_cases
"""
from django.core.management.base import BaseCommand
from cases.models import Case


CONSULTING_CASES = [
    {
        "title": "TechCo Market Entry",
        "prompt": "TechCo, a mid-sized software company, is considering entering the European market. How should they approach this expansion?",
        "context": {
            "client": "TechCo Inc.",
            "situation": "Currently operating in North America with $500M annual revenue. Strong product-market fit but limited international presence.",
            "objective": "Develop a market entry strategy for Europe with go-to-market plan and financial projections."
        },
        "exhibits": [
            {
                "title": "Financial Overview",
                "type": "table",
                "data": {
                    "columns": ["Region", "Revenue", "Growth Rate", "Market Share"],
                    "rows": [
                        ["North America", "$500M", "15%", "12%"],
                        ["Europe", "$0M", "N/A", "N/A"],
                        ["APAC", "$0M", "N/A", "N/A"]
                    ]
                }
            },
            {
                "title": "European Market Size by Segment",
                "type": "bar",
                "data": {
                    "labels": ["Enterprise", "Mid-Market", "SMB"],
                    "values": [50, 30, 20],
                    "unit": "$B"
                }
            },
            {
                "title": "Growth Rate Comparison",
                "type": "table",
                "data": {
                    "columns": ["Segment", "Market Size", "Growth Rate"],
                    "rows": [
                        ["Enterprise", "$50B", "8%"],
                        ["Mid-Market", "$30B", "12%"],
                        ["SMB", "$20B", "20%"]
                    ]
                }
            }
        ]
    },
    {
        "title": "RetailCo Profitability",
        "prompt": "RetailCo's operating margin has declined from 12% to 8% over the past two years. What's driving this decline and how can they recover?",
        "context": {
            "client": "RetailCo Ltd.",
            "situation": "Mature retail chain with 500+ stores. Facing margin pressure from e-commerce and changing consumer behavior.",
            "objective": "Identify root causes of profitability decline and develop a turnaround plan."
        },
        "exhibits": [
            {
                "title": "P&L Trend (Last 3 Years)",
                "type": "table",
                "data": {
                    "columns": ["Year", "Revenue", "COGS", "OpEx", "Operating Margin"],
                    "rows": [
                        ["2022", "$2B", "60%", "28%", "12%"],
                        ["2023", "$2.1B", "62%", "30%", "8%"],
                        ["2024 YTD", "$1.05B", "64%", "32%", "4%"]
                    ]
                }
            },
            {
                "title": "Sales by Channel",
                "type": "pie",
                "data": {
                    "labels": ["Physical Stores", "E-commerce", "Other"],
                    "values": [70, 25, 5],
                    "unit": "%"
                }
            },
            {
                "title": "Channel Performance Details",
                "type": "table",
                "data": {
                    "columns": ["Channel", "% of Sales", "Margin"],
                    "rows": [
                        ["Physical Stores", "70%", "15%"],
                        ["E-commerce", "25%", "-5%"],
                        ["Other", "5%", "10%"]
                    ]
                }
            }
        ]
    },
    {
        "title": "FinTech Pricing Strategy",
        "prompt": "A FinTech startup has two pricing models for their B2B payments platform. Which should they pursue and why?",
        "context": {
            "client": "PayFlow Technologies",
            "situation": "Early-stage FinTech with 50+ enterprise customers. Currently on flat fee model, exploring transaction-based pricing.",
            "objective": "Analyze pricing models and recommend optimal strategy for scaling."
        },
        "exhibits": [
            {
                "title": "Pricing Model Comparison",
                "type": "table",
                "data": {
                    "columns": ["Model", "Customer LTV", "Churn Rate", "Scalability"],
                    "rows": [
                        ["Flat Fee ($5k/month)", "$180k", "8%", "Low"],
                        ["Transaction (0.5%)", "$240k", "12%", "High"],
                        ["Hybrid", "$220k", "6%", "Medium"]
                    ]
                }
            },
            {
                "title": "Customer Base Distribution",
                "type": "pie",
                "data": {
                    "labels": ["SMB", "Mid-Market", "Enterprise"],
                    "values": [36, 46, 18],
                    "unit": "%"
                }
            },
            {
                "title": "Customer Segments",
                "type": "table",
                "data": {
                    "columns": ["Segment", "Avg Volume", "Count", "Retention"],
                    "rows": [
                        ["Enterprise", "$5M/month", "10", "95%"],
                        ["Mid-Market", "$500k/month", "25", "85%"],
                        ["SMB", "$50k/month", "20", "70%"]
                    ]
                }
            },
            {
                "title": "Customer Retention by Segment",
                "type": "bar",
                "data": {
                    "labels": ["Enterprise", "Mid-Market", "SMB"],
                    "values": [95, 85, 70],
                    "unit": "% Retention"
                }
            }
        ]
    },
    {
        "title": "HealthCare Supply Chain",
        "prompt": "A major healthcare provider's supply chain costs have increased 20% YoY. Analyze the issues and propose solutions.",
        "context": {
            "client": "HealthCare Plus",
            "situation": "Network of 30 hospitals across 5 states. Supply chain costs now represent 35% of total operating expenses.",
            "objective": "Reduce supply chain costs by 15-20% while maintaining service quality."
        },
        "exhibits": [
            {
                "title": "Supply Chain Cost Breakdown",
                "type": "pie",
                "data": {
                    "labels": ["Procurement", "Logistics", "Warehousing", "Other"],
                    "values": [40, 35, 15, 10],
                    "unit": "%"
                }
            },
            {
                "title": "Year-over-Year Cost Growth",
                "type": "bar",
                "data": {
                    "labels": ["Procurement", "Logistics", "Warehousing", "Other"],
                    "values": [25, 18, 12, 8],
                    "unit": "% Change"
                }
            },
            {
                "title": "Supplier Concentration",
                "type": "table",
                "data": {
                    "columns": ["Supplier", "% of Spend", "Contract Term"],
                    "rows": [
                        ["Top 5 Combined", "60%", "Fixed until 2026"],
                        ["Others", "40%", "Negotiable"]
                    ]
                }
            }
        ]
    },
    {
        "title": "ManufactureCo Capacity",
        "prompt": "ManufactureCo is operating at 95% capacity utilization but demand is growing 25% annually. Should they invest in new capacity?",
        "context": {
            "client": "ManufactureCo LLC",
            "situation": "Specialty manufacturing firm with flagship facility. Supplier to automotive and aerospace sectors.",
            "objective": "Determine optimal capacity strategy: expand, outsource, or both."
        },
        "exhibits": [
            {
                "title": "Capacity & Demand Analysis",
                "type": "table",
                "data": {
                    "columns": ["Year", "Capacity (units)", "Demand", "Utilization"],
                    "rows": [
                        ["2024", "100k", "95k", "95%"],
                        ["2025F", "100k", "120k", "120%"],
                        ["2026F", "100k", "150k", "150%"]
                    ]
                }
            },
            {
                "title": "Demand vs Capacity Trend",
                "type": "bar",
                "data": {
                    "labels": ["2024", "2025F", "2026F"],
                    "values": [95, 120, 150],
                    "unit": "k units"
                }
            },
            {
                "title": "Expansion Options",
                "type": "table",
                "data": {
                    "columns": ["Option", "Capex", "Lead Time", "Flexibility"],
                    "rows": [
                        ["New Facility", "$50M", "24 months", "High"],
                        ["Outsource", "$0M", "3 months", "Low"],
                        ["Upgrade Existing", "$15M", "12 months", "Medium"]
                    ]
                }
            }
        ]
    }
]

PRODUCT_MANAGEMENT_CASES = [
    {
        "title": "StreamApp New Feature Roadmap",
        "prompt": "StreamApp (music streaming) has 3 feature ideas competing for Q1 resources. How would you prioritize and why?",
        "context": {
            "client": "StreamApp Inc.",
            "situation": "50M users, $200M ARR, competitive market (Spotify, Apple Music). Growth slowing to 12% YoY.",
            "objective": "Develop a data-driven feature prioritization framework and recommend the top 2 features for Q1."
        },
        "exhibits": [
            {
                "title": "Feature Candidates",
                "type": "table",
                "data": {
                    "columns": ["Feature", "Dev Effort", "Potential Impact", "User Demand"],
                    "rows": [
                        ["AI Playlist Generator", "High", "Medium", "High"],
                        ["Podcast Integration", "Medium", "High", "Medium"],
                        ["Family Plans (Tier)", "Medium", "High", "High"]
                    ]
                }
            },
            {
                "title": "User Engagement Metrics",
                "type": "table",
                "data": {
                    "columns": ["Metric", "Current", "Playlist Users", "Podcast Listeners"],
                    "rows": [
                        ["Monthly Engagement", "85%", "+12%", "+8%"],
                        ["Avg Session Duration", "35 min", "+5 min", "+2 min"],
                        ["Churn Rate", "2.5%", "-0.8%", "-0.2%"]
                    ]
                }
            }
        ]
    },
    {
        "title": "Zoo.Co New Product Line",
        "prompt": "Zoo.Co (e-commerce pet supplies) is considering launching a subscription box. What are the key questions to validate before launch?",
        "context": {
            "client": "Zoo.Co Ltd.",
            "situation": "Online pet supplies retailer. $50M revenue, 500k customers. Average order value $40, repeat purchase rate 60%.",
            "objective": "Evaluate subscription box opportunity and develop launch strategy."
        },
        "exhibits": [
            {
                "title": "Market Opportunity",
                "type": "table",
                "data": {
                    "columns": ["Segment", "TAM", "CAGR", "Penetration"],
                    "rows": [
                        ["Pet Subscription Boxes", "$5B", "25%", "15%"],
                        ["Total Pet Market", "$130B", "8%", "N/A"]
                    ]
                }
            },
            {
                "title": "Customer Distribution",
                "type": "pie",
                "data": {
                    "labels": ["Dog Owners", "Cat Owners", "Other Pets"],
                    "values": [60, 35, 5],
                    "unit": "%"
                }
            },
            {
                "title": "Customer Analysis",
                "type": "table",
                "data": {
                    "columns": ["Segment", "% of Customers", "Avg LTV", "Sub Box Intent"],
                    "rows": [
                        ["Dog Owners", "60%", "$800", "45%"],
                        ["Cat Owners", "35%", "$600", "35%"],
                        ["Other Pets", "5%", "$400", "20%"]
                    ]
                }
            },
            {
                "title": "Subscription Box Interest by Segment",
                "type": "bar",
                "data": {
                    "labels": ["Dog Owners", "Cat Owners", "Other Pets"],
                    "values": [45, 35, 20],
                    "unit": "% Intent"
                }
            }
        ]
    },
    {
        "title": "CloudDrive Storage Tiers",
        "prompt": "CloudDrive (cloud storage) has 10M free users but only 5% convert to paid. How would you redesign the pricing/tier strategy?",
        "context": {
            "client": "CloudDrive Technologies",
            "situation": "10M free users (2GB), 500k paid users ($120 ARR average). Competitor Dropbox has 50% freemium conversion.",
            "objective": "Increase freemium-to-paid conversion from 5% to 12% within 12 months."
        },
        "exhibits": [
            {
                "title": "Conversion Funnel",
                "type": "table",
                "data": {
                    "columns": ["Stage", "Users", "Conversion %"],
                    "rows": [
                        ["Free Users", "10M", "100%"],
                        ["Reached Storage Limit", "3M", "30%"],
                        ["Converted to Paid", "500k", "5%"]
                    ]
                }
            },
            {
                "title": "User Funnel Drop-off",
                "type": "bar",
                "data": {
                    "labels": ["Free Users", "Hit Limit", "Converted"],
                    "values": [10.0, 3.0, 0.5],
                    "unit": "M Users"
                }
            },
            {
                "title": "Pricing Options Analysis",
                "type": "table",
                "data": {
                    "columns": ["Tier", "Storage", "Price/Month", "Est. Conversion"],
                    "rows": [
                        ["Current Free", "2GB", "$0", "5%"],
                        ["Tier 1", "100GB", "$2.99", "8%"],
                        ["Tier 2", "1TB", "$9.99", "12%"],
                        ["Tier 3", "2TB", "$19.99", "15%"]
                    ]
                }
            }
        ]
    },
    {
        "title": "EdTech Course Platform",
        "prompt": "An EdTech startup is deciding between B2C (direct to students) vs B2B2C (through schools). Which should they prioritize?",
        "context": {
            "client": "LearnHub Technologies",
            "situation": "Online course platform with 100k free users. Early revenue from 50 schools as pilots. VC-funded, Series A just closed.",
            "objective": "Choose primary go-to-market strategy and develop 18-month growth plan."
        },
        "exhibits": [
            {
                "title": "Market Comparison",
                "type": "table",
                "data": {
                    "columns": ["Channel", "TAM", "CAC", "LTV", "Sales Cycle"],
                    "rows": [
                        ["B2C Direct", "$20B", "$50", "$1000", "3 months"],
                        ["B2B2C Schools", "$15B", "$5k", "$500k", "12 months"],
                        ["B2B2C Corporates", "$10B", "$20k", "$1M", "9 months"]
                    ]
                }
            },
            {
                "title": "Pilot Results (School Channel)",
                "type": "table",
                "data": {
                    "columns": ["Metric", "Value"],
                    "rows": [
                        ["Schools in Pilot", "50"],
                        ["Students Using Platform", "50k"],
                        ["Avg Revenue per School", "$10k/year"],
                        ["Pilot Satisfaction", "8.5/10"]
                    ]
                }
            }
        ]
    },
    {
        "title": "FitnessPro Wearable App",
        "prompt": "FitnessPro launched a fitness tracking app. Current retention is 20% after 30 days. How would you improve this?",
        "context": {
            "client": "FitnessPro Inc.",
            "situation": "Fitness wearable company with 2M active users. App retention poor, but hardware sales strong. Considering app monetization.",
            "objective": "Increase 30-day retention from 20% to 50% and develop app monetization strategy."
        },
        "exhibits": [
            {
                "title": "App Retention Funnel",
                "type": "table",
                "data": {
                    "columns": ["Stage", "Users", "Retention %"],
                    "rows": [
                        ["Install", "2M", "100%"],
                        ["Day 7", "800k", "40%"],
                        ["Day 30", "400k", "20%"],
                        ["Day 90", "100k", "5%"]
                    ]
                }
            },
            {
                "title": "Retention Drop-off Over Time",
                "type": "bar",
                "data": {
                    "labels": ["Install", "Day 7", "Day 30", "Day 90"],
                    "values": [100, 40, 20, 5],
                    "unit": "% Retained"
                }
            },
            {
                "title": "Feature Usage Distribution",
                "type": "bar",
                "data": {
                    "labels": ["Activity Tracking", "Social Challenges", "AI Coach", "Premium Content"],
                    "values": [95, 25, 10, 5],
                    "unit": "% Users"
                }
            },
            {
                "title": "Feature Usage Details",
                "type": "table",
                "data": {
                    "columns": ["Feature", "% of Users", "Engagement Score"],
                    "rows": [
                        ["Activity Tracking", "95%", "8.5"],
                        ["Social Challenges", "25%", "7.0"],
                        ["Premium Content", "5%", "9.0"],
                        ["AI Coach", "10%", "8.0"]
                    ]
                }
            }
        ]
    }
]


class Command(BaseCommand):
    help = 'Seed 10 pre-defined case study scenarios into the database (5 consulting, 5 product management).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing cases before seeding'
        )

    def handle(self, *args, **options):
        if options['clear']:
            Case.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Cleared all existing cases.'))

        # Check if cases already exist
        existing_count = Case.objects.count()
        if existing_count > 0:
            self.stdout.write(
                self.style.WARNING(
                    f'Database already has {existing_count} cases. Use --clear to start fresh.'
                )
            )
            return

        # Seed consulting cases
        for case_data in CONSULTING_CASES:
            case = Case.objects.create(
                title=case_data['title'],
                case_type='consulting',
                prompt=case_data['prompt'],
                context=case_data['context'],
                exhibits=case_data['exhibits'],
                generated_by=None
            )
            self.stdout.write(f'✓ Created: {case.title}')

        # Seed product management cases
        for case_data in PRODUCT_MANAGEMENT_CASES:
            case = Case.objects.create(
                title=case_data['title'],
                case_type='product_management',
                prompt=case_data['prompt'],
                context=case_data['context'],
                exhibits=case_data['exhibits'],
                generated_by=None
            )
            self.stdout.write(f'✓ Created: {case.title}')

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Successfully seeded 10 case studies (5 consulting, 5 product management).'
            )
        )
