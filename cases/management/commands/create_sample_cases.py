"""
Django management command to create 10 sample cases covering various industries.
"""
from django.core.management.base import BaseCommand
from cases.models import Case


class Command(BaseCommand):
    help = 'Creates 10 sample cases covering various industries'

    def handle(self, *args, **options):
        # Delete existing sample cases if they exist (optional - comment out if you want to keep them)
        # Case.objects.filter(generated_by__isnull=True).delete()
        
        cases_data = [
            {
                'title': 'CPG Brand Portfolio Optimization',
                'case_type': Case.CONSULTING,
                'prompt': 'A major CPG company is considering whether to divest one of its underperforming brands. The brand has been losing market share for the past 3 years, but still generates $50M in annual revenue. Should they divest, invest to turn it around, or maintain the status quo?',
                'context': {
                    'client': 'Global Consumer Goods Inc. (GCG)',
                    'situation': 'GCG owns 15 brands across food, beverages, and personal care. One brand, "FreshChoice", has seen declining sales (-5% CAGR) while competitors are growing. The brand represents 8% of total portfolio revenue.',
                    'objective': 'Determine the optimal strategy for FreshChoice: divest, invest, or maintain.'
                },
                'exhibits': [
                    {
                        'title': 'Exhibit 1: FreshChoice Financial Performance',
                        'type': 'table',
                        'data': {
                            'columns': ['Year', 'Revenue ($M)', 'EBITDA Margin (%)', 'Market Share (%)'],
                            'rows': [
                                ['2021', '55', '12', '15'],
                                ['2022', '52', '10', '14'],
                                ['2023', '50', '8', '13']
                            ]
                        }
                    },
                    {
                        'title': 'Exhibit 2: Competitive Landscape',
                        'type': 'table',
                        'data': {
                            'columns': ['Competitor', 'Market Share (%)', 'Revenue Growth (%)'],
                            'rows': [
                                ['Brand A', '25', '8'],
                                ['Brand B', '20', '6'],
                                ['FreshChoice', '13', '-5'],
                                ['Brand C', '12', '4']
                            ]
                        }
                    }
                ]
            },
            {
                'title': 'Automotive Market Entry Strategy',
                'case_type': Case.CONSULTING,
                'prompt': 'An automotive manufacturer wants to enter the electric vehicle (EV) market in Southeast Asia. They need to decide: which countries to enter first, what vehicle segments to target, and whether to build new factories or partner with local manufacturers.',
                'context': {
                    'client': 'AutoGlobal Motors',
                    'situation': 'AutoGlobal is a traditional ICE vehicle manufacturer with strong presence in North America and Europe. They have limited EV experience and no presence in Southeast Asia. The region has 650M people and growing middle class.',
                    'objective': 'Develop a market entry strategy for EV business in Southeast Asia.'
                },
                'exhibits': [
                    {
                        'title': 'Exhibit 1: Southeast Asia Market Size',
                        'type': 'table',
                        'data': {
                            'columns': ['Country', 'Population (M)', 'EV Penetration (%)', 'GDP per Capita ($)'],
                            'rows': [
                                ['Thailand', '70', '2', '7,800'],
                                ['Indonesia', '275', '0.5', '4,300'],
                                ['Vietnam', '98', '1', '3,700'],
                                ['Malaysia', '33', '1.5', '11,400']
                            ]
                        }
                    },
                    {
                        'title': 'Exhibit 2: Investment Requirements',
                        'type': 'table',
                        'data': {
                            'columns': ['Option', 'Initial Investment ($M)', 'Time to Market (years)', 'Capacity (units/year)'],
                            'rows': [
                                ['Build New Factory', '500', '3', '50,000'],
                                ['Acquire Local Factory', '300', '1.5', '30,000'],
                                ['Joint Venture', '200', '2', '40,000']
                            ]
                        }
                    }
                ]
            },
            {
                'title': 'Pharmaceutical Market Entry',
                'case_type': Case.CONSULTING,
                'prompt': 'A biotech company has developed a breakthrough drug for a rare disease affecting 50,000 patients globally. They need to determine pricing strategy, distribution channels, and whether to commercialize independently or partner with a larger pharma company.',
                'context': {
                    'client': 'BioPharm Innovations',
                    'situation': 'BioPharm has spent $200M developing a novel treatment for a rare genetic disorder. The drug has shown 80% efficacy in clinical trials. The company has no commercial infrastructure and limited capital.',
                    'objective': 'Develop a go-to-market strategy for the new drug.'
                },
                'exhibits': [
                    {
                        'title': 'Exhibit 1: Patient Population by Region',
                        'type': 'table',
                        'data': {
                            'columns': ['Region', 'Patients', 'Avg. Income ($)', 'Insurance Coverage (%)'],
                            'rows': [
                                ['North America', '20,000', '45,000', '85'],
                                ['Europe', '18,000', '38,000', '90'],
                                ['Asia Pacific', '10,000', '12,000', '60'],
                                ['Other', '2,000', '8,000', '40']
                            ]
                        }
                    },
                    {
                        'title': 'Exhibit 2: Competitive Treatments',
                        'type': 'table',
                        'data': {
                            'columns': ['Treatment', 'Efficacy (%)', 'Annual Cost ($)', 'Market Share (%)'],
                            'rows': [
                                ['Current Standard', '40', '50,000', '100'],
                                ['BioPharm Drug', '80', 'TBD', '0']
                            ]
                        }
                    }
                ]
            },
            {
                'title': 'Oil & Gas Profitability Challenge',
                'case_type': Case.CONSULTING,
                'prompt': 'An oil & gas company is experiencing declining profitability in its upstream operations. Production costs have increased 30% over 3 years while oil prices have been volatile. They need to identify cost reduction opportunities and optimize their portfolio.',
                'context': {
                    'client': 'EnergyCorp International',
                    'situation': 'EnergyCorp operates 25 oil fields across 5 countries. EBITDA margins have declined from 35% to 22% over 3 years. The company is considering divesting non-core assets or investing in efficiency improvements.',
                    'objective': 'Improve upstream profitability by 10 percentage points within 2 years.'
                },
                'exhibits': [
                    {
                        'title': 'Exhibit 1: Field Performance Summary',
                        'type': 'table',
                        'data': {
                            'columns': ['Field Type', 'Count', 'Avg. Production Cost ($/barrel)', 'EBITDA Margin (%)'],
                            'rows': [
                                ['Onshore', '15', '35', '28'],
                                ['Offshore Shallow', '6', '42', '20'],
                                ['Offshore Deep', '4', '58', '12']
                            ]
                        }
                    },
                    {
                        'title': 'Exhibit 2: Cost Breakdown',
                        'type': 'table',
                        'data': {
                            'columns': ['Cost Category', 'Percentage of Total', '3-Year Change (%)'],
                            'rows': [
                                ['Labor', '35', '+15'],
                                ['Equipment', '25', '+20'],
                                ['Maintenance', '20', '+40'],
                                ['Other', '20', '+25']
                            ]
                        }
                    }
                ]
            },
            {
                'title': 'Tech SaaS Pricing Strategy',
                'case_type': Case.CONSULTING,
                'prompt': 'A B2B SaaS company is losing customers to competitors offering lower prices. They need to decide whether to lower prices, introduce a freemium tier, or differentiate through features. Current pricing is $99/user/month.',
                'context': {
                    'client': 'CloudTech Solutions',
                    'situation': 'CloudTech provides project management software to mid-market companies (50-500 employees). They have 5,000 customers but churn rate increased from 5% to 12% in the last year. Competitors offer similar products at $49-79/user/month.',
                    'objective': 'Develop a pricing strategy to reduce churn and maintain profitability.'
                },
                'exhibits': [
                    {
                        'title': 'Exhibit 1: Customer Segmentation',
                        'type': 'table',
                        'data': {
                            'columns': ['Segment', 'Customers', 'Avg. Users', 'Churn Rate (%)', 'LTV ($)'],
                            'rows': [
                                ['Small (50-100)', '2,000', '25', '15', '18,000'],
                                ['Mid (101-250)', '2,500', '75', '10', '54,000'],
                                ['Large (251-500)', '500', '200', '8', '144,000']
                            ]
                        }
                    },
                    {
                        'title': 'Exhibit 2: Competitive Pricing',
                        'type': 'table',
                        'data': {
                            'columns': ['Competitor', 'Price ($/user/month)', 'Features', 'Market Share (%)'],
                            'rows': [
                                ['CloudTech', '99', 'Full Suite', '25'],
                                ['Competitor A', '79', 'Core Features', '30'],
                                ['Competitor B', '49', 'Basic', '20'],
                                ['Competitor C', '89', 'Full Suite', '25']
                            ]
                        }
                    }
                ]
            },
            {
                'title': 'Retail Expansion Decision',
                'case_type': Case.CONSULTING,
                'prompt': 'A retail chain wants to expand into a new geographic market. They need to evaluate whether to open physical stores, launch e-commerce only, or use a hybrid model. The target market has 10M people with growing disposable income.',
                'context': {
                    'client': 'RetailMax Corporation',
                    'situation': 'RetailMax operates 200 stores in North America selling home goods and furniture. They are considering expansion into Latin America. The company has strong e-commerce capabilities but no physical presence in the region.',
                    'objective': 'Determine the optimal expansion strategy for Latin America.'
                },
                'exhibits': [
                    {
                        'title': 'Exhibit 1: Market Opportunity',
                        'type': 'table',
                        'data': {
                            'columns': ['Country', 'Population (M)', 'GDP per Capita ($)', 'E-commerce Penetration (%)'],
                            'rows': [
                                ['Brazil', '215', '8,500', '12'],
                                ['Mexico', '130', '9,800', '8'],
                                ['Argentina', '45', '10,200', '10'],
                                ['Colombia', '51', '6,400', '6']
                            ]
                        }
                    },
                    {
                        'title': 'Exhibit 2: Investment Comparison',
                        'type': 'table',
                        'data': {
                            'columns': ['Model', 'Initial Investment ($M)', 'Year 3 Revenue ($M)', 'Break-even (years)'],
                            'rows': [
                                ['Physical Stores (10)', '50', '80', '4'],
                                ['E-commerce Only', '15', '40', '2'],
                                ['Hybrid (5 stores + online)', '35', '70', '3']
                            ]
                        }
                    }
                ]
            },
            {
                'title': 'Banking Digital Transformation',
                'case_type': Case.CONSULTING,
                'prompt': 'A traditional bank is losing younger customers to digital-only banks. They need to decide whether to build their own digital platform, acquire a fintech company, or partner with a tech provider. Current digital adoption is 30% vs. 60% for competitors.',
                'context': {
                    'client': 'Heritage Bank',
                    'situation': 'Heritage Bank has 500 branches and 5M customers, but only 1.5M use digital banking. Customer acquisition cost has increased 40% while digital banks are growing 3x faster. Average customer age is 52.',
                    'objective': 'Increase digital adoption to 50% and reduce customer acquisition cost by 25%.'
                },
                'exhibits': [
                    {
                        'title': 'Exhibit 1: Customer Demographics',
                        'type': 'table',
                        'data': {
                            'columns': ['Age Group', 'Customers (M)', 'Digital Adoption (%)', 'Avg. Revenue ($)'],
                            'rows': [
                                ['18-35', '1.5', '45', '200'],
                                ['36-50', '2.0', '35', '400'],
                                ['51-65', '1.2', '20', '600'],
                                ['65+', '0.3', '10', '500']
                            ]
                        }
                    },
                    {
                        'title': 'Exhibit 2: Digital Strategy Options',
                        'type': 'table',
                        'data': {
                            'columns': ['Option', 'Investment ($M)', 'Time to Launch (months)', 'Expected Adoption (%)'],
                            'rows': [
                                ['Build In-house', '100', '24', '45'],
                                ['Acquire Fintech', '250', '6', '55'],
                                ['Partner with Tech Co', '50', '12', '40']
                            ]
                        }
                    }
                ]
            },
            {
                'title': 'Manufacturing Cost Optimization',
                'case_type': Case.CONSULTING,
                'prompt': 'A manufacturing company is facing margin pressure due to rising material and labor costs. They need to identify cost reduction opportunities across their supply chain, operations, and overhead. Target: reduce COGS by 15%.',
                'context': {
                    'client': 'Industrial Manufacturing Co.',
                    'situation': 'IMC produces industrial equipment with 5 factories across 3 countries. Material costs increased 25% and labor costs increased 18% over 2 years. Current gross margin is 22%, down from 30% two years ago.',
                    'objective': 'Reduce cost of goods sold (COGS) by 15% to restore profitability.'
                },
                'exhibits': [
                    {
                        'title': 'Exhibit 1: Cost Structure',
                        'type': 'table',
                        'data': {
                            'columns': ['Cost Category', 'Percentage', '2-Year Change (%)'],
                            'rows': [
                                ['Raw Materials', '45', '+25'],
                                ['Labor', '30', '+18'],
                                ['Overhead', '15', '+12'],
                                ['Other', '10', '+8']
                            ]
                        }
                    },
                    {
                        'title': 'Exhibit 2: Factory Performance',
                        'type': 'table',
                        'data': {
                            'columns': ['Factory', 'Location', 'Capacity Utilization (%)', 'Cost per Unit ($)'],
                            'rows': [
                                ['Factory A', 'USA', '85', '120'],
                                ['Factory B', 'Mexico', '75', '95'],
                                ['Factory C', 'China', '90', '80'],
                                ['Factory D', 'USA', '70', '130'],
                                ['Factory E', 'Mexico', '80', '100']
                            ]
                        }
                    }
                ]
            },
            {
                'title': 'Healthcare Provider Strategy',
                'case_type': Case.CONSULTING,
                'prompt': 'A hospital system is evaluating whether to expand services, acquire smaller clinics, or focus on specialization. They operate 8 hospitals with $2B in annual revenue but face competition from specialized centers.',
                'context': {
                    'client': 'Metro Health System',
                    'situation': 'Metro Health operates 8 hospitals serving a metropolitan area of 3M people. Market share has declined from 35% to 28% over 5 years. Specialized centers (cardiac, cancer) are capturing high-margin procedures.',
                    'objective': 'Develop a growth strategy to increase market share to 35% and improve margins.'
                },
                'exhibits': [
                    {
                        'title': 'Exhibit 1: Service Line Performance',
                        'type': 'table',
                        'data': {
                            'columns': ['Service Line', 'Revenue ($M)', 'Margin (%)', 'Market Share (%)'],
                            'rows': [
                                ['General Medicine', '800', '8', '30'],
                                ['Cardiac Care', '400', '15', '25'],
                                ['Cancer Treatment', '300', '20', '20'],
                                ['Emergency', '500', '5', '35']
                            ]
                        }
                    },
                    {
                        'title': 'Exhibit 2: Growth Options',
                        'type': 'table',
                        'data': {
                            'columns': ['Option', 'Investment ($M)', 'Expected Revenue ($M)', 'Payback (years)'],
                            'rows': [
                                ['Build Cardiac Center', '150', '80', '5'],
                                ['Acquire 5 Clinics', '100', '60', '4'],
                                ['Specialize in Cancer', '200', '120', '6']
                            ]
                        }
                    }
                ]
            },
            {
                'title': 'Airlines Profitability Turnaround',
                'case_type': Case.CONSULTING,
                'prompt': 'An airline is struggling with profitability due to high fuel costs and intense competition. They need to optimize routes, adjust pricing, and potentially restructure operations. Current operating margin is -2%.',
                'context': {
                    'client': 'Global Airways',
                    'situation': 'Global Airways operates 150 aircraft serving 80 destinations. Fuel costs represent 35% of operating expenses. Load factor is 78% (industry average: 82%). The airline has lost money for 2 consecutive years.',
                    'objective': 'Achieve positive operating margin of 5% within 18 months.'
                },
                'exhibits': [
                    {
                        'title': 'Exhibit 1: Route Performance',
                        'type': 'table',
                        'data': {
                            'columns': ['Route Type', 'Routes', 'Avg. Load Factor (%)', 'Profit Margin (%)'],
                            'rows': [
                                ['Domestic Short', '40', '82', '3'],
                                ['Domestic Long', '25', '75', '-1'],
                                ['International', '15', '72', '-3']
                            ]
                        }
                    },
                    {
                        'title': 'Exhibit 2: Cost Structure',
                        'type': 'table',
                        'data': {
                            'columns': ['Cost Category', 'Percentage', 'vs. Industry Avg (%)'],
                            'rows': [
                                ['Fuel', '35', '+5'],
                                ['Labor', '25', '+3'],
                                ['Aircraft', '20', '0'],
                                ['Other', '20', '-2']
                            ]
                        }
                    }
                ]
            }
        ]
        
        created_count = 0
        for case_data in cases_data:
            # Check if case already exists
            if not Case.objects.filter(title=case_data['title']).exists():
                Case.objects.create(**case_data)
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created: {case_data["title"]}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Skipped (already exists): {case_data["title"]}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\nSuccessfully created {created_count} sample cases!')
        )

