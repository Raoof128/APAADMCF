-- Australian Privacy Act ADM Compliance Framework - Database Schema
-- PostgreSQL 14+

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =============================================================================
-- USERS & ROLES
-- =============================================================================

CREATE TYPE user_role AS ENUM (
    'admin',
    'privacy_officer',
    'compliance_auditor',
    'data_scientist',
    'individual_request_manager',
    'read_only_viewer'
);

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role user_role NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- =============================================================================
-- ADM SYSTEM REGISTRY
-- =============================================================================

CREATE TYPE adm_category AS ENUM (
    'fully_automated',
    'partially_automated',
    'human_in_the_loop'
);

CREATE TYPE decision_impact AS ENUM (
    'low',
    'medium',
    'high',
    'critical'
);

CREATE TYPE system_status AS ENUM (
    'development',
    'testing',
    'production',
    'deprecated',
    'decommissioned'
);

CREATE TABLE adm_systems (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    owner_id UUID REFERENCES users(id),
    purpose TEXT NOT NULL,
    adm_category adm_category NOT NULL,
    decision_impact decision_impact NOT NULL,
    system_status system_status DEFAULT 'development',
    model_type VARCHAR(100), -- 'classification', 'regression', 'rule_based', etc.
    deployment_date DATE,
    last_review_date DATE,
    next_review_date DATE,
    data_retention_period INTEGER, -- in days
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id)
);

CREATE INDEX idx_adm_systems_owner ON adm_systems(owner_id);
CREATE INDEX idx_adm_systems_impact ON adm_systems(decision_impact);
CREATE INDEX idx_adm_systems_status ON adm_systems(system_status);
CREATE INDEX idx_adm_systems_metadata ON adm_systems USING GIN(metadata);

-- =============================================================================
-- DATA CATEGORIES
-- =============================================================================

CREATE TYPE data_sensitivity AS ENUM (
    'public',
    'internal',
    'confidential',
    'sensitive', -- APP definition of sensitive
    'highly_sensitive'
);

CREATE TABLE data_categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    sensitivity data_sensitivity NOT NULL,
    is_pii BOOLEAN DEFAULT FALSE,
    is_sensitive_info BOOLEAN DEFAULT FALSE, -- Under Privacy Act
    legal_basis TEXT,
    retention_period INTEGER, -- in days
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE adm_system_data_categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    adm_system_id UUID REFERENCES adm_systems(id) ON DELETE CASCADE,
    data_category_id UUID REFERENCES data_categories(id) ON DELETE CASCADE,
    purpose TEXT,
    is_input BOOLEAN DEFAULT TRUE,
    is_output BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(adm_system_id, data_category_id)
);

CREATE INDEX idx_adm_data_cat_system ON adm_system_data_categories(adm_system_id);
CREATE INDEX idx_adm_data_cat_category ON adm_system_data_categories(data_category_id);

-- =============================================================================
-- PRIVACY IMPACT ASSESSMENT (PIA)
-- =============================================================================

CREATE TYPE pia_status AS ENUM (
    'draft',
    'in_review',
    'approved',
    'rejected',
    'requires_revision'
);

CREATE TABLE pia_assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    adm_system_id UUID REFERENCES adm_systems(id) ON DELETE CASCADE,
    version INTEGER DEFAULT 1,
    status pia_status DEFAULT 'draft',

    -- Purpose & Necessity Test
    purpose_description TEXT,
    necessity_justification TEXT,
    purpose_score INTEGER CHECK (purpose_score BETWEEN 0 AND 100),

    -- Data Minimisation (APP3)
    data_minimisation_assessment TEXT,
    data_minimisation_score INTEGER CHECK (data_minimisation_score BETWEEN 0 AND 100),

    -- Consent/Notification (APP5)
    consent_mechanism TEXT,
    notification_method TEXT,
    consent_score INTEGER CHECK (consent_score BETWEEN 0 AND 100),

    -- Reasonable Expectations
    reasonable_expectations_analysis TEXT,
    reasonable_expectations_score INTEGER CHECK (reasonable_expectations_score BETWEEN 0 AND 100),

    -- Sensitive Information Test
    sensitive_info_used BOOLEAN,
    sensitive_info_justification TEXT,
    sensitive_info_score INTEGER CHECK (sensitive_info_score BETWEEN 0 AND 100),

    -- Overall Assessment
    overall_risk_level decision_impact,
    overall_score INTEGER CHECK (overall_score BETWEEN 0 AND 100),
    recommendations TEXT,

    -- Approval
    assessor_id UUID REFERENCES users(id),
    reviewer_id UUID REFERENCES users(id),
    approver_id UUID REFERENCES users(id),
    assessment_date DATE,
    review_date DATE,
    approval_date DATE,
    next_review_date DATE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_pia_adm_system ON pia_assessments(adm_system_id);
CREATE INDEX idx_pia_status ON pia_assessments(status);

-- =============================================================================
-- RISK ITEMS
-- =============================================================================

CREATE TYPE risk_severity AS ENUM (
    'low',
    'medium',
    'high',
    'critical'
);

CREATE TYPE risk_status AS ENUM (
    'identified',
    'assessing',
    'mitigating',
    'accepted',
    'closed'
);

CREATE TABLE risk_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pia_assessment_id UUID REFERENCES pia_assessments(id) ON DELETE CASCADE,
    adm_system_id UUID REFERENCES adm_systems(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    risk_category VARCHAR(100), -- 'bias', 'privacy', 'security', 'fairness', etc.
    severity risk_severity NOT NULL,
    likelihood INTEGER CHECK (likelihood BETWEEN 1 AND 5),
    impact INTEGER CHECK (impact BETWEEN 1 AND 5),
    risk_score INTEGER GENERATED ALWAYS AS (likelihood * impact) STORED,
    status risk_status DEFAULT 'identified',
    owner_id UUID REFERENCES users(id),
    identified_date DATE,
    target_closure_date DATE,
    actual_closure_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_risk_items_pia ON risk_items(pia_assessment_id);
CREATE INDEX idx_risk_items_system ON risk_items(adm_system_id);
CREATE INDEX idx_risk_items_severity ON risk_items(severity);
CREATE INDEX idx_risk_items_status ON risk_items(status);

-- =============================================================================
-- MITIGATION TASKS
-- =============================================================================

CREATE TYPE mitigation_status AS ENUM (
    'planned',
    'in_progress',
    'completed',
    'on_hold',
    'cancelled'
);

CREATE TABLE mitigation_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    risk_item_id UUID REFERENCES risk_items(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status mitigation_status DEFAULT 'planned',
    assigned_to UUID REFERENCES users(id),
    priority INTEGER CHECK (priority BETWEEN 1 AND 5),
    due_date DATE,
    completion_date DATE,
    effort_estimate INTEGER, -- in hours
    actual_effort INTEGER, -- in hours
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_mitigation_risk ON mitigation_tasks(risk_item_id);
CREATE INDEX idx_mitigation_assigned ON mitigation_tasks(assigned_to);
CREATE INDEX idx_mitigation_status ON mitigation_tasks(status);

-- =============================================================================
-- EVIDENCE ITEMS
-- =============================================================================

CREATE TABLE evidence_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pia_assessment_id UUID REFERENCES pia_assessments(id) ON DELETE CASCADE,
    risk_item_id UUID REFERENCES risk_items(id) ON DELETE CASCADE,
    mitigation_task_id UUID REFERENCES mitigation_tasks(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    file_path VARCHAR(500),
    file_type VARCHAR(50),
    file_size BIGINT,
    uploaded_by UUID REFERENCES users(id),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_evidence_pia ON evidence_items(pia_assessment_id);
CREATE INDEX idx_evidence_risk ON evidence_items(risk_item_id);
CREATE INDEX idx_evidence_mitigation ON evidence_items(mitigation_task_id);

-- =============================================================================
-- FAIRNESS & BIAS METRICS
-- =============================================================================

CREATE TABLE fairness_assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    adm_system_id UUID REFERENCES adm_systems(id) ON DELETE CASCADE,
    assessment_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    dataset_name VARCHAR(255),
    dataset_size INTEGER,
    protected_attributes JSONB, -- array of protected attribute names

    -- Fairness Metrics
    demographic_parity NUMERIC(5,4),
    equal_opportunity NUMERIC(5,4),
    predictive_parity NUMERIC(5,4),
    error_rate_ratio NUMERIC(5,4),
    statistical_parity_difference NUMERIC(5,4),
    disparate_impact NUMERIC(5,4),

    -- Overall Assessment
    fairness_score INTEGER CHECK (fairness_score BETWEEN 0 AND 100),
    is_high_risk BOOLEAN DEFAULT FALSE,
    findings TEXT,
    recommendations TEXT,

    assessor_id UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_fairness_adm_system ON fairness_assessments(adm_system_id);
CREATE INDEX idx_fairness_date ON fairness_assessments(assessment_date);

CREATE TABLE explainability_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    fairness_assessment_id UUID REFERENCES fairness_assessments(id) ON DELETE CASCADE,
    adm_system_id UUID REFERENCES adm_systems(id) ON DELETE CASCADE,
    method VARCHAR(50), -- 'SHAP', 'LIME', etc.
    feature_importance JSONB,
    sample_explanations JSONB,
    visualization_path VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_explainability_fairness ON explainability_results(fairness_assessment_id);
CREATE INDEX idx_explainability_system ON explainability_results(adm_system_id);

-- =============================================================================
-- INDIVIDUAL REQUESTS
-- =============================================================================

CREATE TYPE request_type AS ENUM (
    'explanation',
    'human_review',
    'correction',
    'access',
    'deletion',
    'complaint'
);

CREATE TYPE request_status AS ENUM (
    'submitted',
    'acknowledged',
    'in_progress',
    'pending_information',
    'completed',
    'rejected',
    'withdrawn'
);

CREATE TABLE individual_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    request_type request_type NOT NULL,
    status request_status DEFAULT 'submitted',

    -- Requester Information (encrypted)
    requester_name VARCHAR(255),
    requester_email VARCHAR(255),
    requester_phone VARCHAR(50),

    -- Request Details
    adm_system_id UUID REFERENCES adm_systems(id),
    decision_reference VARCHAR(255),
    decision_date DATE,
    request_description TEXT,

    -- Workflow
    assigned_to UUID REFERENCES users(id),
    priority INTEGER CHECK (priority BETWEEN 1 AND 5) DEFAULT 3,

    -- SLA Tracking
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    due_date TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,

    -- Response
    response_summary TEXT,
    response_details TEXT,
    response_file_path VARCHAR(500),

    -- Audit
    created_by UUID REFERENCES users(id),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_requests_status ON individual_requests(status);
CREATE INDEX idx_requests_type ON individual_requests(request_type);
CREATE INDEX idx_requests_assigned ON individual_requests(assigned_to);
CREATE INDEX idx_requests_adm_system ON individual_requests(adm_system_id);
CREATE INDEX idx_requests_submitted ON individual_requests(submitted_at);

CREATE TABLE request_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    request_id UUID REFERENCES individual_requests(id) ON DELETE CASCADE,
    status request_status NOT NULL,
    notes TEXT,
    changed_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_request_history_request ON request_history(request_id);

-- =============================================================================
-- COMPLIANCE MONITORING
-- =============================================================================

CREATE TYPE alert_severity AS ENUM (
    'info',
    'warning',
    'error',
    'critical'
);

CREATE TYPE alert_status AS ENUM (
    'active',
    'acknowledged',
    'investigating',
    'resolved',
    'false_positive'
);

CREATE TABLE compliance_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    adm_system_id UUID REFERENCES adm_systems(id) ON DELETE CASCADE,
    alert_type VARCHAR(100), -- 'drift', 'bias', 'policy_violation', etc.
    severity alert_severity NOT NULL,
    status alert_status DEFAULT 'active',
    title VARCHAR(255) NOT NULL,
    description TEXT,
    metrics JSONB,
    threshold_value NUMERIC,
    actual_value NUMERIC,

    -- Workflow
    assigned_to UUID REFERENCES users(id),
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolution_notes TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_alerts_system ON compliance_alerts(adm_system_id);
CREATE INDEX idx_alerts_severity ON compliance_alerts(severity);
CREATE INDEX idx_alerts_status ON compliance_alerts(status);
CREATE INDEX idx_alerts_type ON compliance_alerts(alert_type);
CREATE INDEX idx_alerts_created ON compliance_alerts(created_at);

CREATE TABLE drift_detections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    adm_system_id UUID REFERENCES adm_systems(id) ON DELETE CASCADE,
    detection_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    drift_type VARCHAR(50), -- 'data', 'model', 'concept'
    drift_score NUMERIC(5,4),
    baseline_metrics JSONB,
    current_metrics JSONB,
    features_affected JSONB,
    is_significant BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_drift_system ON drift_detections(adm_system_id);
CREATE INDEX idx_drift_date ON drift_detections(detection_date);
CREATE INDEX idx_drift_type ON drift_detections(drift_type);

-- =============================================================================
-- AUDIT LOGS
-- =============================================================================

CREATE TYPE audit_action AS ENUM (
    'create',
    'read',
    'update',
    'delete',
    'approve',
    'reject',
    'export',
    'login',
    'logout'
);

CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    action audit_action NOT NULL,
    resource_type VARCHAR(100), -- 'adm_system', 'pia', 'request', etc.
    resource_id UUID,
    ip_address INET,
    user_agent TEXT,
    request_path VARCHAR(500),
    request_method VARCHAR(10),
    status_code INTEGER,
    changes JSONB, -- before/after values
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_action ON audit_logs(action);
CREATE INDEX idx_audit_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_created ON audit_logs(created_at);

-- Prevent deletion/modification of audit logs
CREATE RULE audit_log_immutable AS ON UPDATE TO audit_logs DO INSTEAD NOTHING;
CREATE RULE audit_log_no_delete AS ON DELETE TO audit_logs DO INSTEAD NOTHING;

-- =============================================================================
-- TRANSPARENCY & NOTIFICATIONS
-- =============================================================================

CREATE TABLE transparency_notices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    adm_system_id UUID REFERENCES adm_systems(id) ON DELETE CASCADE,
    version INTEGER DEFAULT 1,

    -- APP5 Compliance Fields
    collection_notice TEXT,
    purpose_statement TEXT,
    data_usage_explanation TEXT,
    decision_explanation TEXT,
    rights_explanation TEXT,
    review_process_explanation TEXT,
    contact_information TEXT,

    -- Metadata
    language VARCHAR(10) DEFAULT 'en',
    is_active BOOLEAN DEFAULT TRUE,
    published_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,

    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_transparency_system ON transparency_notices(adm_system_id);
CREATE INDEX idx_transparency_active ON transparency_notices(is_active);

-- =============================================================================
-- WORKFLOWS
-- =============================================================================

CREATE TYPE workflow_status AS ENUM (
    'pending',
    'in_progress',
    'completed',
    'cancelled'
);

CREATE TABLE workflows (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workflow_type VARCHAR(100), -- 'pia_approval', 'annual_review', etc.
    entity_type VARCHAR(100),
    entity_id UUID,
    status workflow_status DEFAULT 'pending',
    current_step VARCHAR(100),
    steps JSONB,
    assigned_to UUID REFERENCES users(id),
    due_date TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_workflows_status ON workflows(status);
CREATE INDEX idx_workflows_entity ON workflows(entity_type, entity_id);
CREATE INDEX idx_workflows_assigned ON workflows(assigned_to);

-- =============================================================================
-- REPORTING & ANALYTICS
-- =============================================================================

CREATE TABLE compliance_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    report_type VARCHAR(100), -- 'oaic', 'internal', 'fairness_audit', etc.
    report_period_start DATE,
    report_period_end DATE,
    generated_by UUID REFERENCES users(id),
    file_path VARCHAR(500),
    file_format VARCHAR(20),
    summary JSONB,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_reports_type ON compliance_reports(report_type);
CREATE INDEX idx_reports_created ON compliance_reports(created_at);

-- =============================================================================
-- VIEWS FOR COMMON QUERIES
-- =============================================================================

-- Active high-risk ADM systems
CREATE VIEW v_high_risk_adm_systems AS
SELECT
    a.*,
    p.overall_risk_level,
    p.overall_score as pia_score,
    COUNT(DISTINCT r.id) as open_risk_count
FROM adm_systems a
LEFT JOIN pia_assessments p ON a.id = p.adm_system_id AND p.status = 'approved'
LEFT JOIN risk_items r ON a.id = r.adm_system_id AND r.status NOT IN ('closed', 'accepted')
WHERE a.is_active = TRUE
  AND a.decision_impact IN ('high', 'critical')
GROUP BY a.id, p.overall_risk_level, p.overall_score;

-- Overdue mitigation tasks
CREATE VIEW v_overdue_mitigations AS
SELECT
    m.*,
    r.title as risk_title,
    r.severity as risk_severity,
    a.name as adm_system_name,
    u.full_name as assigned_to_name
FROM mitigation_tasks m
JOIN risk_items r ON m.risk_item_id = r.id
JOIN adm_systems a ON r.adm_system_id = a.id
LEFT JOIN users u ON m.assigned_to = u.id
WHERE m.status NOT IN ('completed', 'cancelled')
  AND m.due_date < CURRENT_DATE;

-- SLA compliance for individual requests
CREATE VIEW v_request_sla_status AS
SELECT
    ir.*,
    a.name as adm_system_name,
    u.full_name as assigned_to_name,
    CASE
        WHEN ir.completed_at IS NOT NULL THEN
            EXTRACT(EPOCH FROM (ir.completed_at - ir.submitted_at))/3600
        ELSE
            EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - ir.submitted_at))/3600
    END as hours_elapsed,
    CASE
        WHEN ir.due_date IS NOT NULL AND ir.completed_at IS NULL AND CURRENT_TIMESTAMP > ir.due_date THEN TRUE
        WHEN ir.due_date IS NOT NULL AND ir.completed_at IS NOT NULL AND ir.completed_at > ir.due_date THEN TRUE
        ELSE FALSE
    END as is_overdue
FROM individual_requests ir
LEFT JOIN adm_systems a ON ir.adm_system_id = a.id
LEFT JOIN users u ON ir.assigned_to = u.id;

-- =============================================================================
-- FUNCTIONS & TRIGGERS
-- =============================================================================

-- Update timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to all relevant tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_adm_systems_updated_at BEFORE UPDATE ON adm_systems
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_pia_updated_at BEFORE UPDATE ON pia_assessments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_risks_updated_at BEFORE UPDATE ON risk_items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_mitigations_updated_at BEFORE UPDATE ON mitigation_tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_requests_updated_at BEFORE UPDATE ON individual_requests
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_alerts_updated_at BEFORE UPDATE ON compliance_alerts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_workflows_updated_at BEFORE UPDATE ON workflows
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_transparency_updated_at BEFORE UPDATE ON transparency_notices
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Auto-set SLA due dates for individual requests (30 days default)
CREATE OR REPLACE FUNCTION set_request_due_date()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.due_date IS NULL THEN
        NEW.due_date = NEW.submitted_at + INTERVAL '30 days';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_individual_request_due_date
    BEFORE INSERT ON individual_requests
    FOR EACH ROW EXECUTE FUNCTION set_request_due_date();

-- =============================================================================
-- SEED DATA
-- =============================================================================

-- Insert default data categories
INSERT INTO data_categories (name, description, sensitivity, is_pii, is_sensitive_info) VALUES
('Name', 'Individual full name', 'confidential', TRUE, FALSE),
('Email Address', 'Email contact information', 'confidential', TRUE, FALSE),
('Phone Number', 'Telephone contact information', 'confidential', TRUE, FALSE),
('Date of Birth', 'Individual date of birth', 'confidential', TRUE, FALSE),
('Address', 'Physical residential address', 'confidential', TRUE, FALSE),
('Government ID', 'Passport, drivers license, etc.', 'highly_sensitive', TRUE, TRUE),
('Financial Information', 'Bank account, credit card, income', 'highly_sensitive', TRUE, TRUE),
('Health Information', 'Medical records, health status', 'highly_sensitive', TRUE, TRUE),
('Racial/Ethnic Origin', 'Racial or ethnic background', 'highly_sensitive', TRUE, TRUE),
('Political Opinions', 'Political views or affiliations', 'highly_sensitive', TRUE, TRUE),
('Religious Beliefs', 'Religious or philosophical beliefs', 'highly_sensitive', TRUE, TRUE),
('Sexual Orientation', 'Sexual orientation or practices', 'highly_sensitive', TRUE, TRUE),
('Criminal Record', 'Criminal history or allegations', 'highly_sensitive', TRUE, TRUE),
('Biometric Data', 'Fingerprints, facial recognition', 'highly_sensitive', TRUE, TRUE),
('Location Data', 'GPS coordinates, movement patterns', 'confidential', TRUE, FALSE),
('Behavioural Data', 'Online behaviour, preferences', 'internal', TRUE, FALSE),
('Credit Score', 'Credit rating information', 'highly_sensitive', TRUE, TRUE),
('Employment History', 'Work history and references', 'confidential', TRUE, FALSE);

-- Insert default admin user (password: Admin123! - should be changed)
INSERT INTO users (email, hashed_password, full_name, role) VALUES
('admin@example.gov.au', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYWHiN4hQ5W', 'System Administrator', 'admin');

COMMENT ON TABLE adm_systems IS 'Central registry of all automated decision-making systems';
COMMENT ON TABLE pia_assessments IS 'Privacy Impact Assessments for ADM systems';
COMMENT ON TABLE risk_items IS 'Identified privacy and compliance risks';
COMMENT ON TABLE individual_requests IS 'Requests from individuals for explanation, review, or correction';
COMMENT ON TABLE compliance_alerts IS 'Automated alerts for drift, bias, and policy violations';
COMMENT ON TABLE audit_logs IS 'Immutable audit trail of all system actions';
