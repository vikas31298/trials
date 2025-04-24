import utils.projectretrievers as r
from utils.projectmodels import ProjectDataRetriever, DocumentSchema, Page, Tag

project_report_schema = DocumentSchema(
    pages=[
        Page(
            page_number=1,
            tags=[
                Tag(id="project_name", title="Project Name", variations=[]),
                Tag(id="client", title="client name", variations=[]),
                Tag(id="pricing_model", title="Pricing Model", variations=[]),
            ],
        ),
        Page(
            page_number=2,
            tags=[
                Tag(
                    id="project_revenue", title="Project Revenue Total", source="Project revenue calculations", variations=[]
                ),
                Tag(id="project_revenue_growth_mom", title="Sales Growth Mom", source="Airtable Product Sales", variations=[]),
                Tag(id="gross_margin", title="Gross Margin Total", variations=[]),
                Tag(id="executive_summary", title="Executive Summary", variations=[]),
                Tag(id="customer_retention", title="Customer Retention", source="Airtable CSAT", variations=[]),
                Tag(id="new_customers", title="New Customers", source="Airtable CSAT", variations=[]),
            ],
        ),
        Page(
            page_number=3,
            tags=[
                Tag(
                    id="sales_revenue", title="Sales Revenue Total", variations=[]
                ),
                Tag(id="sales_revenue_ly", title="Sales Revenue Ly", variations=[]),
                Tag(
                    id="sales_revenue_prevmo",
                    title="Sales Revenue Prevmo",
                    variations=[],
                ),
                Tag(id="sales_growth_mom", title="Sales Growth Mom", variations=[]),
                Tag(
                    id="sales_growth_mom_prevmo",
                    title="Sales Growth Mom Prevmo",
                    variations=[],
                ),
                Tag(
                    id="sales_growth_mom_ly", title="Sales Growth Mom Ly", variations=[]
                ),
                Tag(
                    id="gross_margin_prevmo",
                    title="Gross Margin Prevmo",
                    variations=[],
                ),
                Tag(
                    id="gross_margin_ly",
                    title="Gross Margin Ly",
                    variations=[],
                ),
                Tag(
                    id="sales_growth_yoy",
                    title="Sales Growth Yoy",
                    variations=[],
                ),
                Tag(
                    id="sales_growth_yoy_prevmo",
                    title="Sales Growth Yoy Prevmo",
                    variations=[],
                ),
                Tag(
                    id="sales_growth_yoy_ly",
                    title="Sales Growth Yoy Ly",
                    variations=[],
                ),
                Tag(
                    id="gross_margin",
                    title="Gross Margin",
                    variations=[],
                ),
                Tag(id="fin_perf_bullets", title="Financial Performance Bullets", variations=[]),
                Tag(
                    id="month",
                    title="Month",
                    variations=[],
                ),
                Tag(
                    id="year",
                    title="Year",
                    variations=[],
                ),
            ],
        ),
        Page(
            page_number=4,
            tags=[
                Tag(
                    id="product_sales_bullets",
                    title="Product Sales Bullets",
                    variations=[],
                ),
                # Tag(
                #     id="category_sales_chart",
                #     title="Category Sales Chart",
                #     variations=[],
                # ),
            ],
        ),
        Page(
            page_number=5,
            tags=[
                Tag(
                    id="product_sales",
                    title="Product Sales Table",
                    variations=[],
                ),
            ],
        ),
        Page(
            page_number=6,
            tags=[
                Tag(
                    id="recommendations_intro",
                    title="Recommendations Intro",
                    variations=[],
                ),
                Tag(
                    id="recommendation_bullets",
                    title="Recommendation Bullets",
                    variations=[],
                ),
            ],
        ),
    ],
)


project_report_retrievers = {
    "executive_summary": {
        "retriever": (r._get_executive_summary, 
                      (lambda self: 5, lambda self: 2024, lambda self: "self.department", lambda self: "self.company")),
        "multiple_values": True
    },
    "sales_revenue": {
        "retriever": (
            r._get_project_revenue,
            (lambda self: 5, lambda self: 2024, lambda self: "self.company"),
        ),
        "multiple_values": False
    },
    "sales_revenue_prevmo": {
        "retriever": (
            r._get_project_revenue,
            (lambda self: 4, lambda self: 2024, lambda self: "self.company"),
        ),
        "multiple_values": False
    },
    "sales_revenue_ly": {
        "retriever": (
            r._get_project_revenue,
            (lambda self: 4, lambda self: 2024, lambda self: "self.company"),
        ),
        "multiple_values": False
    },
    "project_revenue_growth_mom": {
        "retriever": (
            r._get_project_revenue_growth_mom,
            (lambda self: 5, lambda self: 2024, lambda self: "self.company"),
        ),
        "multiple_values": False
    },
    "sales_growth_mom_prevmo": {
        "retriever": (
            r._get_project_revenue_growth_mom,
            (lambda self: 4, lambda self: 2024, lambda self: "self.company"),
        ),
        "multiple_values": False
    },
    "sales_growth_mom_ly": {
        "retriever": (
            r._get_project_revenue_growth_mom,
            (lambda self: 4, lambda self: 2024, lambda self: "self.company"),
        ),
        "multiple_values": False
    },
    "gross_margin": {
        "retriever": (
            r._get_gross_margin,
             (lambda self: 5, lambda self: 2024, lambda self: "self.company"),
        ),
        "multiple_values": False
    },
    "gross_margin_prevmo": {
        "retriever": (
            r._get_gross_margin,
            (lambda self: 4, lambda self: 2024, lambda self: "self.company"),
        ),
        "multiple_values": False
    },
    "gross_margin_ly": {
        "retriever": (
            r._get_gross_margin,
            (lambda self: 4, lambda self: 2024, lambda self: "self.company"),
        ),
        "multiple_values": False
    },
    "sales_growth_yoy": {
        "retriever": (
            r._get_project_revenue_growth_yoy,    
            (lambda self: 5, lambda self: 2024, lambda self: "self.company"),
        ),
        "multiple_values": False
    },
    "sales_growth_yoy_prevmo": {
        "retriever": (
            r._get_project_revenue_growth_yoy,
            (lambda self: 4, lambda self: 2024, lambda self: "self.company"),
        ),
        "multiple_values": False
    },
    "sales_growth_yoy_ly": {
        "retriever": (
            r._get_project_revenue_growth_yoy,
            (lambda self: 4, lambda self: 2024, lambda self: "self.company"),
        ),
        "multiple_values": False
    },
    "customer_retention": {
        "retriever": (
            r._get_customer_data,
            (
                lambda self: 5,
                lambda self: 2024,
                "Customer Retention Rate (%)",
            ),
        ),
        "multiple_values": False
    },
    "new_customers": {
        "retriever": (
            r._get_customer_data,
            (
                lambda self: 4,
                lambda self: 2024,
                "Customer Acquisition Rate (%)",
            ),
        ),
        "multiple_values": False
    },
    "fin_perf_bullets": {
        "retriever": (r._get_fin_perf_bullets, 
                      (lambda self: 5, 
                       lambda self: 2024, 
                       lambda self: "self.company")),
        "multiple_values": True
    },
    "product_sales": {
        "retriever": (
            r._get_product_sales_table,
            (lambda self: 5, 
             lambda self: 2024, 
             lambda self: "self.company"),
        ),
        "multiple_values": False
    },
    "product_sales_bullets": {
        "retriever": (
            r._get_product_sales_bullets,
            (lambda self: 4, lambda self: 2024, lambda self: "self.company"),
        ),
        "multiple_values": True
    },
    "category_sales_chart": {
        "retriever": (
            r._get_category_sales_chart,
            (lambda self: 5, 
             lambda self: 2024, 
             lambda self: "self.company"),
        ),
        "multiple_values": False
    },
    "recommendations_intro": {
        "retriever": (r._get_recommendations_intro, 
                      (lambda self: 5, 
                       lambda self: 2024, 
                       lambda self: "self.department", 
                       lambda self: "self.company")),
        "multiple_values": True
    },
    "recommendation_bullets": {
        "retriever": (r._get_recommendation_bullets, 
                      (lambda self: 5, 
                       lambda self: 2024, 
                       lambda self: "self.company")),
        "multiple_values": True
    },
    "month": {
        "retriever": (lambda self: 5),
        "multiple_values": False
    },
    "month_short": {
        "retriever": (lambda self: "May"),
        "multiple_values": False
    },
    "pricing_model": {
        "retriever": (lambda self: self.pricing_model),
        "multiple_values": False
    },
    "project_name": {
        "retriever": (lambda self: self.project_name),
        "multiple_values": False
    },
    "client": {
        "retriever": (lambda self: self.client),
        "multiple_values": False
    },
    "year": {
        "retriever": (lambda self: self.year),
        "multiple_values": False
    },
    "department": {
        "retriever": (lambda self: self.department),
        "multiple_values": False
    },
    "project_revenue": {
        "retriever": (lambda self: self.project_revenue),
        "multiple_values": False
    },
}
