"""Tender data models used by parsers, DOCX generators and Excel generators."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class EquipmentItem:
    sl_no: int
    equipment_type: str
    minimum_number: str


@dataclass
class ManpowerItem:
    sl_no: int
    post: str
    qualification: str
    nos: str
    total_exp: str
    similar_exp: str


@dataclass
class BOQItem:
    item_no: int
    item_code: str
    description: str
    quantity: float
    unit: str
    bwdb_rate: float
    bwdb_amount: float
    quoted_rate: float
    quoted_amount: float
    percent_diff: float


@dataclass
class WorkActivity:
    sl_no: str
    activity: str


@dataclass
class JVPartner:
    code: str = ""
    name: str = ""
    legal_type: str = ""
    address: str = ""
    signatory_name: str = ""
    position: str = ""
    role: str = "partner"
    share_percent: float = 0.0
    share_words: str = ""


@dataclass
class TenderData:
    tender_id: str
    invitation_ref_no: str
    package_no: str
    project_code: str
    procuring_entity: str
    procuring_entity_short: str
    executive_engineer: str
    pe_address: str
    pe_division: str
    work_name: str
    work_name_short: str
    location: str
    project_name: str
    publication_date: str
    closing_date: str
    start_date: str
    completion_date: str
    completion_date_long: str
    bg_validity_date: str
    document_date: str
    tender_security_amount: float
    tender_security_amount_words: str
    tender_security_bdt: str
    liquid_assets_required_lakh: float
    annual_turnover_required_lakh: float
    tender_capacity_lakh: float
    document_fee_bdt: float
    quoted_rate_percent: float
    departmental_estimate: float
    quoted_total: float
    general_exp_years: int
    specific_exp_contracts: int
    specific_exp_value_lakh: float
    specific_exp_years: int
    specific_exp_nature: str
    bank_name: str
    bank_branch: str
    bank_guarantee_no: str
    bg_date: str
    firm_name: str
    firm_address: str
    proprietor_name: str
    egp_email: str
    memo_no: str
    is_jv: bool = False
    jv_name: str = ""
    jv_date: str = ""
    jv_partner_count: int = 0
    jv_share_text: str = ""
    jv_partners: List[JVPartner] = field(default_factory=list)
    jv_office_address: str = ""
    jv_phone: str = ""
    lead_partner: str = ""
    nominated_partner: str = ""
    partner_in_charge_name: str = ""
    partner_in_charge_firm: str = ""
    partner1_code: str = ""
    partner1_firm_name: str = ""
    partner1_legal_type: str = ""
    partner1_address: str = ""
    partner1_signatory_name: str = ""
    partner1_position: str = ""
    partner1_share_percent: float = 0.0
    partner1_share_words: str = ""
    partner2_code: str = ""
    partner2_firm_name: str = ""
    partner2_legal_type: str = ""
    partner2_address: str = ""
    partner2_signatory_name: str = ""
    partner2_position: str = ""
    partner2_share_percent: float = 0.0
    partner2_share_words: str = ""
    partner3_code: str = ""
    partner3_firm_name: str = ""
    partner3_legal_type: str = ""
    partner3_address: str = ""
    partner3_signatory_name: str = ""
    partner3_position: str = ""
    partner3_share_percent: float = 0.0
    partner3_share_words: str = ""
    equipment: List[EquipmentItem] = field(default_factory=list)
    manpower: List[ManpowerItem] = field(default_factory=list)
    boq_items: List[BOQItem] = field(default_factory=list)
    rate_schedule_ref: str = "BWDB, 2019-20 Rate Schedule"
    work_activities: List[WorkActivity] = field(default_factory=list)
    work_start_year: int = 2021
    work_end_year: int = 2022
    work_months: List[str] = field(default_factory=list)
