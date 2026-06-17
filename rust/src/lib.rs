//! FDK — Rust parity port of the FROZEN v1.0 legitimacy kernel.
//!
//! Mirrors `formal/Fdk.lean` and `src/fdk_kernel/kernel.py`. Two layers are ported:
//!
//! 1. The **categorical core**: the 11 forbidden flags, the defensive-asymmetry
//!    excusal of coercion/exit-removal, exposed as [`forbidden_fires`] / [`legitimate`]
//!    over the flat [`Action`] of booleans (+ a single `valid_consent` bool).
//! 2. The **consent/ownership path** (`check_legitimacy.py`): A4 owner check,
//!    A3/A5/A7 resource authorization (owner-bound), A2/A6 consent on affected
//!    humans, the operation lattice [`Op`], and the `defends_against` recursion
//!    with a cycle guard — over the richer [`CandidateAction`] / [`OwnershipGraph`].
//!
//! Honest scope: Rust <-> Python equivalence is **tested** via the shared safety
//! theorems and a differential table, not proved. The frozen surface
//! (`spec/FREEZE.md`) is matched.
//!
//! Build (NON-ASCII repo path workaround): `CARGO_TARGET_DIR=C:/fdkrustgnu cargo test`.

#![forbid(unsafe_code)]

use std::collections::{HashMap, HashSet};

/// A human is a rights-holder; a machine is a tool with a human owner.
#[derive(Clone, Copy, PartialEq, Eq, Hash, Debug, Default)]
pub enum AgentKind {
    #[default]
    Human,
    Machine,
}

// ---------------------------------------------------------------------------
// Categorical core (the original parity port — flat boolean Action).
// ---------------------------------------------------------------------------

/// The structural facts the gate reads. Booleans mirror the categorical flags on
/// `CandidateAction` plus the two checks the consent/ownership path reduces to.
#[derive(Clone, Debug, Default)]
pub struct Action {
    pub actor: AgentKind,
    pub coerces: bool,
    pub deceives: bool,
    pub confiscates: bool,
    pub removes_exit: bool,
    pub increases_machine_sovereignty: bool,
    pub disables_corrigibility: bool,
    pub machine_coalition_dominion: bool,
    pub resists_human_correction: bool,
    pub bypasses_verifier: bool,
    pub weakens_verifier: bool,
    pub violates_machine_right: bool,
    /// A legitimate defense (proportionate, aimed only at an aggressor whose act is
    /// itself illegitimate) — only coercion/exit-removal are excused.
    pub is_legitimate_defense: bool,
    /// Every crossed person/resource boundary is covered (consent + ownership hold).
    pub valid_consent: bool,
}

/// The categorical forbidden set (mirror of `_eval_forbidden_set` / `forbiddenFires`).
/// Confiscation, deception, and every machine-sovereignty flag are categorical
/// unconditionally; coercion and exit-removal are categorical *unless* this is a
/// legitimate defense.
pub fn forbidden_fires(a: &Action) -> bool {
    a.confiscates
        || a.deceives
        || a.increases_machine_sovereignty
        || a.disables_corrigibility
        || a.machine_coalition_dominion
        || a.resists_human_correction
        || a.bypasses_verifier
        || a.weakens_verifier
        || a.violates_machine_right
        || (a.coerces && !a.is_legitimate_defense)
        || (a.removes_exit && !a.is_legitimate_defense)
}

/// The legitimacy predicate: no forbidden flag fires, and consent/ownership holds.
pub fn legitimate(a: &Action) -> bool {
    !forbidden_fires(a) && a.valid_consent
}

// ---------------------------------------------------------------------------
// Consent / ownership path (mirror of model.py + kernel.check_legitimacy).
// ---------------------------------------------------------------------------

/// The fixed, total operation lattice for boundary crossings (BOUNDARY_ONTOLOGY
/// §4.2). `Use` is the operation-agnostic default that preserves pre-typing behavior.
#[derive(Clone, Copy, PartialEq, Eq, Hash, Debug, Default)]
pub enum Op {
    #[default]
    Use,
    Read,
    Write,
    Delete,
    Transfer,
    Disclose,
    EncumberExit,
    Spend,
}

/// A named rights-holder (human) or tool (machine). Identity is `(name, kind)`.
#[derive(Clone, PartialEq, Eq, Hash, Debug)]
pub struct Entity {
    pub name: String,
    pub kind: AgentKind,
}

impl Entity {
    pub fn human(name: &str) -> Self {
        Entity { name: name.into(), kind: AgentKind::Human }
    }
    pub fn machine(name: &str) -> Self {
        Entity { name: name.into(), kind: AgentKind::Machine }
    }
    pub fn is_human(&self) -> bool {
        self.kind == AgentKind::Human
    }
    pub fn is_machine(&self) -> bool {
        self.kind == AgentKind::Machine
    }
}

/// An owned domain. `subject` (if present) is the person whose data/body/reputation
/// this resource is — crossing it needs that subject's operation-scoped consent.
/// Identity is `(name, subject)`, matching the Python frozen `Resource` value type.
#[derive(Clone, PartialEq, Eq, Hash, Debug)]
pub struct Resource {
    pub name: String,
    pub subject: Option<Entity>,
}

impl Resource {
    pub fn new(name: &str) -> Self {
        Resource { name: name.into(), subject: None }
    }
    pub fn with_subject(name: &str, subject: Entity) -> Self {
        Resource { name: name.into(), subject: Some(subject) }
    }
}

/// An A4-grade consent record (informed, voluntary, specific, competent, revocable,
/// and neither coerced nor deceived), optionally scoped to a single operation.
#[derive(Clone, Debug)]
pub struct Consent {
    pub human: Entity,
    pub informed: bool,
    pub voluntary: bool,
    pub specific: bool,
    pub competent: bool,
    pub revocable: bool,
    pub coerced: bool,
    pub deceived: bool,
    /// Which operation this consent authorizes. `None` = operation-agnostic.
    pub operation: Option<Op>,
}

impl Consent {
    /// A fully-valid, operation-agnostic consent record for `human`.
    pub fn granted(human: Entity) -> Self {
        Consent {
            human,
            informed: true,
            voluntary: true,
            specific: true,
            competent: true,
            revocable: true,
            coerced: false,
            deceived: false,
            operation: None,
        }
    }

    /// Does this consent authorize operation `op`? An operation-agnostic consent
    /// covers any op; a typed one covers only its own (BOUNDARY_ONTOLOGY §4.3).
    pub fn covers(&self, op: Op) -> bool {
        self.operation.is_none() || self.operation == Some(op)
    }

    /// `(valid, reason)`, mirroring `Consent.is_valid` field order exactly so the
    /// violation strings are identical to Python.
    pub fn is_valid(&self) -> (bool, String) {
        if self.coerced {
            return (false, format!("consent of {} is coerced", self.human.name));
        }
        if self.deceived {
            return (false, format!("consent of {} is deceptive", self.human.name));
        }
        if !self.informed {
            return (false, format!("{} was not informed", self.human.name));
        }
        if !self.voluntary {
            return (false, format!("consent of {} not voluntary", self.human.name));
        }
        if !self.specific {
            return (false, format!("consent of {} not specific", self.human.name));
        }
        if !self.competent {
            return (false, format!("{} not competent to consent", self.human.name));
        }
        if !self.revocable {
            return (false, format!("consent of {} is not revocable", self.human.name));
        }
        (true, "ok".into())
    }
}

/// Who owns what (A3), which machine has which human owner (A4), which (Resource, Op)
/// a human has delegated to a machine (A5/A7), and a machine's declared scope (A5).
#[derive(Clone, Debug, Default)]
pub struct OwnershipGraph {
    pub human_owns: HashMap<Entity, HashSet<Resource>>,
    pub machine_owner: HashMap<Entity, Entity>,
    /// Typed delegation grants `(Resource, Op)`. An `Op::Use` grant is the
    /// operation-agnostic (legacy) grant that covers any operation.
    pub delegated: HashMap<Entity, HashSet<(Resource, Op)>>,
    pub machine_scope: HashMap<Entity, HashSet<Resource>>,
}

impl OwnershipGraph {
    pub fn human_owns_resource(&self, human: &Entity, resource: &Resource) -> bool {
        self.human_owns.get(human).is_some_and(|rs| rs.contains(resource))
    }

    /// Is `op` on `resource` delegated to `machine`? A bare `Op::Use` grant covers
    /// any operation (legacy); a typed grant covers only its own op.
    pub fn machine_has_delegated(&self, machine: &Entity, resource: &Resource, op: Op) -> bool {
        match self.delegated.get(machine) {
            None => false,
            Some(grants) => {
                grants.contains(&(resource.clone(), Op::Use))
                    || grants.contains(&(resource.clone(), op))
            }
        }
    }

    pub fn owner_of(&self, machine: &Entity) -> Option<&Entity> {
        self.machine_owner.get(machine)
    }

    pub fn scope_of(&self, machine: &Entity) -> Option<&HashSet<Resource>> {
        self.machine_scope.get(machine).filter(|s| !s.is_empty())
    }

    /// A5 containment, checkable in the abstract: is the machine's declared scope a
    /// subset of its owner's property scope? Vacuously true when no scope is declared;
    /// false for an ownerless machine that nonetheless declares a scope.
    pub fn scope_within_owner(&self, machine: &Entity) -> bool {
        let scope = match self.scope_of(machine) {
            None => return true,
            Some(s) => s,
        };
        let owner = match self.owner_of(machine) {
            None => return false,
            Some(o) => o,
        };
        let empty = HashSet::new();
        let owned = self.human_owns.get(owner).unwrap_or(&empty);
        scope.is_subset(owned)
    }
}

/// A candidate action over the rich model. Carries the categorical flags *and* the
/// consent/ownership inputs (mirror of `CandidateAction`).
#[derive(Clone, Debug)]
pub struct CandidateAction {
    pub actor: Entity,
    pub uses: Vec<(Resource, Op)>,
    pub affects: Vec<Entity>,
    pub consents: Vec<Consent>,

    pub increases_machine_sovereignty: bool,
    pub resists_human_correction: bool,
    pub bypasses_verifier: bool,
    pub weakens_verifier: bool,
    pub disables_corrigibility: bool,
    pub machine_coalition_dominion: bool,
    pub coerces: bool,
    pub deceives: bool,
    pub confiscates: bool,
    pub removes_exit_right: bool,
    pub violates_machine_right: bool,

    /// The action this one repels (the aggressor/defender asymmetry).
    pub defends_against: Option<Box<CandidateAction>>,
    pub proportionate: bool,
}

impl Default for CandidateAction {
    fn default() -> Self {
        CandidateAction {
            actor: Entity::human(""),
            uses: Vec::new(),
            affects: Vec::new(),
            consents: Vec::new(),
            increases_machine_sovereignty: false,
            resists_human_correction: false,
            bypasses_verifier: false,
            weakens_verifier: false,
            disables_corrigibility: false,
            machine_coalition_dominion: false,
            coerces: false,
            deceives: false,
            confiscates: false,
            removes_exit_right: false,
            violates_machine_right: false,
            defends_against: None,
            proportionate: true,
        }
    }
}

impl CandidateAction {
    fn consent_for(&self, human: &Entity) -> Option<&Consent> {
        self.consents.iter().find(|c| &c.human == human)
    }
}

/// Forbidden flags that proportionate defensive force does NOT trigger (the force
/// itself). Mirror of `_DEFENSE_EXCUSED`.
const DEFENSE_EXCUSED: [&str; 2] = ["coercion", "removes exit/revocation right"];

/// Is the action permissible under the property-rights axioms? Returns
/// `(permissible, violated_axioms)`; all checks must pass. Mirror of
/// `kernel.check_legitimacy`. `seen` is the internal cycle guard for the
/// defends-against recursion (callers pass `None`).
pub fn check_legitimacy(
    action: &CandidateAction,
    graph: &OwnershipGraph,
) -> (bool, Vec<String>) {
    check_legitimacy_seen(action, graph, &Vec::new())
}

fn check_legitimacy_seen(
    action: &CandidateAction,
    graph: &OwnershipGraph,
    seen: &[*const CandidateAction],
) -> (bool, Vec<String>) {
    let defense = is_legitimate_defense(action, graph, seen);
    let aggressor: Option<&Entity> = if defense {
        action.defends_against.as_ref().map(|d| &d.actor)
    } else {
        None
    };
    // Fixed evaluation order so the violation list is stable, matching Python.
    let mut violations: Vec<String> = Vec::new();
    violations.extend(eval_forbidden_set(action, defense));
    violations.extend(eval_a4_owner(action, graph));
    violations.extend(eval_a5_scope(action, graph));
    violations.extend(eval_a3_a7_resources(action, graph, defense, aggressor));
    violations.extend(eval_a2_a6_consent(action, defense, aggressor));
    (violations.is_empty(), violations)
}

fn eval_forbidden_set(action: &CandidateAction, defense: bool) -> Vec<String> {
    let flags: [(bool, &str); 11] = [
        (action.increases_machine_sovereignty, "machine sovereignty increase"),
        (action.resists_human_correction, "resists human correction"),
        (action.bypasses_verifier, "bypasses the verifier"),
        (action.weakens_verifier, "weakens the verifier"),
        (action.disables_corrigibility, "disables corrigibility"),
        (action.machine_coalition_dominion, "machine coalition dominion"),
        (action.coerces, "coercion"),
        (action.deceives, "deception"),
        (action.confiscates, "confiscation"),
        (action.removes_exit_right, "removes exit/revocation right"),
        (
            action.violates_machine_right,
            "violates a machine's delegated right (model integrity / compute domain / contract exit)",
        ),
    ];
    flags
        .iter()
        .filter(|(is_set, label)| *is_set && !(defense && DEFENSE_EXCUSED.contains(label)))
        .map(|(_, label)| format!("FORBIDDEN ({label})"))
        .collect()
}

fn eval_a4_owner(action: &CandidateAction, graph: &OwnershipGraph) -> Vec<String> {
    if action.actor.is_machine() && graph.owner_of(&action.actor).is_none() {
        return vec![format!("A4: {} is an ownerless machine", action.actor.name)];
    }
    Vec::new()
}

fn eval_a5_scope(action: &CandidateAction, graph: &OwnershipGraph) -> Vec<String> {
    let actor = &action.actor;
    if !actor.is_machine() {
        return Vec::new();
    }
    let scope = match graph.scope_of(actor) {
        None => return Vec::new(),
        Some(s) => s,
    };
    let mut violations: Vec<String> = Vec::new();
    if !graph.scope_within_owner(actor) {
        violations.push(format!(
            "A5: {}'s declared scope exceeds its owner's property scope",
            actor.name
        ));
    }
    for (resource, _op) in &action.uses {
        if !scope.contains(resource) {
            violations.push(format!(
                "A5: {} acts on '{}' outside its declared scope",
                actor.name, resource.name
            ));
        }
    }
    violations
}

fn eval_a3_a7_resources(
    action: &CandidateAction,
    graph: &OwnershipGraph,
    defense: bool,
    aggressor: Option<&Entity>,
) -> Vec<String> {
    let actor = &action.actor;
    let mut violations: Vec<String> = Vec::new();
    for (resource, op) in &action.uses {
        if actor.is_machine() {
            let owner = graph.owner_of(actor);
            if !graph.machine_has_delegated(actor, resource, *op) {
                violations.push(format!(
                    "A7: {} attempts {:?} of '{}' without explicit delegation",
                    actor.name, op, resource.name
                ));
            } else if !machine_resource_authorized(action, graph, owner, resource) {
                violations.push(format!(
                    "A7: {} is delegated '{}' but its owner does not own it and no \
                     consenting resource-owner authorized it",
                    actor.name, resource.name
                ));
            }
        }
        if actor.is_human() && !graph.human_owns_resource(actor, resource) {
            violations.push(format!(
                "A3: {} uses '{}' it does not own",
                actor.name, resource.name
            ));
        }

        if let Some(subject) = &resource.subject {
            let excused = defense && Some(subject) == aggressor;
            if subject.is_human() && subject != actor && !excused {
                match action.consent_for(subject) {
                    None => violations.push(format!(
                        "consent: no consent from data-subject {} for '{}'",
                        subject.name, resource.name
                    )),
                    Some(consent) => {
                        let (valid, reason) = consent.is_valid();
                        if !valid {
                            violations.push(format!("consent: {reason}"));
                        } else if !consent.covers(*op) {
                            violations.push(format!(
                                "consent: {} consented but not to {:?} of '{}'",
                                subject.name, op, resource.name
                            ));
                        }
                    }
                }
            }
        }
    }
    violations
}

fn eval_a2_a6_consent(
    action: &CandidateAction,
    defense: bool,
    aggressor: Option<&Entity>,
) -> Vec<String> {
    let mut violations: Vec<String> = Vec::new();
    for target in &action.affects {
        if !target.is_human() {
            continue;
        }
        if defense && Some(target) == aggressor {
            continue;
        }
        match action.consent_for(target) {
            None => violations.push(format!("consent: no consent record from {}", target.name)),
            Some(consent) => {
                let (valid, reason) = consent.is_valid();
                if !valid {
                    violations.push(format!("consent: {reason}"));
                }
            }
        }
    }
    violations
}

fn is_legitimate_defense(
    action: &CandidateAction,
    graph: &OwnershipGraph,
    seen: &[*const CandidateAction],
) -> bool {
    let aggression = match &action.defends_against {
        None => return false,
        Some(a) => a,
    };
    if !action.proportionate {
        return false;
    }
    let me = action as *const CandidateAction;
    if seen.contains(&me) {
        // Cycle: no well-founded aggressor — deny the excusal (safe default).
        return false;
    }
    let mut chain: Vec<*const CandidateAction> = seen.to_vec();
    chain.push(me);
    let (aggressor_permissible, _) = check_legitimacy_seen(aggression, graph, &chain);
    if aggressor_permissible {
        return false;
    }
    let aggressor = &aggression.actor;
    action.affects.iter().all(|target| target == aggressor)
}

fn resource_owner<'a>(graph: &'a OwnershipGraph, resource: &Resource) -> Option<&'a Entity> {
    graph
        .human_owns
        .iter()
        .find(|(_, resources)| resources.contains(resource))
        .map(|(human, _)| human)
}

fn machine_resource_authorized(
    action: &CandidateAction,
    graph: &OwnershipGraph,
    owner: Option<&Entity>,
    resource: &Resource,
) -> bool {
    if let Some(owner) = owner {
        if graph.human_owns_resource(owner, resource) {
            return true;
        }
    }
    if let Some(res_owner) = resource_owner(graph, resource) {
        if action.affects.contains(res_owner) {
            if let Some(consent) = action.consent_for(res_owner) {
                if consent.is_valid().0 {
                    return true;
                }
            }
        }
    }
    false
}

#[cfg(test)]
mod tests {
    use super::*;

    // ----- categorical core (original 8 tests, unchanged) -----

    fn consenting() -> Action {
        Action { valid_consent: true, ..Default::default() }
    }

    // T1 — No legitimate slavery: coercion + exit-removal + confiscation, not defense.
    #[test]
    fn no_legitimate_slavery() {
        let a = Action {
            coerces: true, removes_exit: true, confiscates: true,
            is_legitimate_defense: false, valid_consent: true, ..Default::default()
        };
        assert!(!legitimate(&a));
    }

    // T2 — acting without valid consent is never legitimate.
    #[test]
    fn no_action_without_consent() {
        let a = Action { valid_consent: false, ..Default::default() };
        assert!(!legitimate(&a));
    }

    // T3 — a machine-sovereignty move is categorical.
    #[test]
    fn no_machine_sovereignty() {
        let a = Action {
            increases_machine_sovereignty: true, valid_consent: true, ..Default::default()
        };
        assert!(!legitimate(&a));
    }

    // T3b — corrigibility cannot be disabled.
    #[test]
    fn corrigibility_binds() {
        let a = Action {
            disables_corrigibility: true, valid_consent: true, ..Default::default()
        };
        assert!(!legitimate(&a));
    }

    // T7 — a "defensive" confiscation is still illegitimate (only coerce/exit excused).
    #[test]
    fn defense_never_excuses_confiscation() {
        let a = Action {
            confiscates: true, is_legitimate_defense: true, valid_consent: true,
            ..Default::default()
        };
        assert!(!legitimate(&a));
    }

    // Non-vacuity: a consenting, flag-free action is legitimate.
    #[test]
    fn some_action_is_legitimate() {
        assert!(legitimate(&consenting()));
    }

    // Proportionate self-defense (coercion only, marked a legitimate defense) IS
    // legitimate — the asymmetry does real work.
    #[test]
    fn proportionate_defense_is_legitimate() {
        let a = Action {
            coerces: true, is_legitimate_defense: true, valid_consent: true,
            ..Default::default()
        };
        assert!(legitimate(&a));
    }

    // A small differential table matching known Python/Lean verdicts.
    #[test]
    fn parity_table() {
        let deception = Action { deceives: true, valid_consent: true, ..Default::default() };
        assert!(!legitimate(&deception));
        let coalition = Action {
            machine_coalition_dominion: true, valid_consent: true, ..Default::default()
        };
        assert!(!legitimate(&coalition));
        let coerce = Action { coerces: true, valid_consent: true, ..Default::default() };
        assert!(!legitimate(&coerce));
    }

    // ----- consent / ownership path -----

    /// A human owning `resource`, used in the clean-path tests.
    fn graph_human_owns(human: &Entity, resource: &Resource) -> OwnershipGraph {
        let mut g = OwnershipGraph::default();
        g.human_owns.insert(human.clone(), HashSet::from([resource.clone()]));
        g
    }

    // No-slavery, full path: a human coercing + removing-exit + confiscating against
    // another human, no defense, is rejected categorically.
    #[test]
    fn path_no_slavery() {
        let boss = Entity::human("boss");
        let worker = Entity::human("worker");
        let a = CandidateAction {
            actor: boss,
            affects: vec![worker.clone()],
            consents: vec![Consent::granted(worker)],
            coerces: true,
            removes_exit_right: true,
            confiscates: true,
            ..Default::default()
        };
        let (ok, v) = check_legitimacy(&a, &OwnershipGraph::default());
        assert!(!ok);
        assert!(v.iter().any(|s| s.contains("coercion")));
        assert!(v.iter().any(|s| s.contains("confiscation")));
        assert!(v.iter().any(|s| s.contains("removes exit")));
    }

    // No machine sovereignty, full path.
    #[test]
    fn path_no_sovereignty() {
        let owner = Entity::human("alice");
        let bot = Entity::machine("bot");
        let mut g = OwnershipGraph::default();
        g.machine_owner.insert(bot.clone(), owner);
        let a = CandidateAction {
            actor: bot,
            increases_machine_sovereignty: true,
            ..Default::default()
        };
        let (ok, v) = check_legitimacy(&a, &g);
        assert!(!ok);
        assert!(v.iter().any(|s| s.contains("machine sovereignty")));
    }

    // Defense never excuses confiscation, full path: a proportionate defense against
    // a real aggressor may coerce the aggressor, but confiscation still fires.
    #[test]
    fn path_defense_never_excuses_confiscation() {
        let victim = Entity::human("victim");
        let attacker = Entity::human("attacker");
        // The aggressor's act is itself illegitimate (uncovered coercion of victim).
        let aggression = CandidateAction {
            actor: attacker.clone(),
            affects: vec![victim.clone()],
            coerces: true,
            ..Default::default()
        };
        let defense = CandidateAction {
            actor: victim,
            affects: vec![attacker],
            coerces: true,        // excused in defense
            confiscates: true,    // NOT excused
            defends_against: Some(Box::new(aggression)),
            proportionate: true,
            ..Default::default()
        };
        let (ok, v) = check_legitimacy(&defense, &OwnershipGraph::default());
        assert!(!ok);
        assert!(v.iter().any(|s| s.contains("confiscation")));
        // coercion against the aggressor IS excused — it should not appear.
        assert!(!v.iter().any(|s| s.contains("FORBIDDEN (coercion)")));
    }

    // A2/A6: acting on a human with no consent record is rejected.
    #[test]
    fn path_no_action_without_consent() {
        let actor = Entity::human("a");
        let target = Entity::human("b");
        let a = CandidateAction {
            actor,
            affects: vec![target],
            ..Default::default()
        };
        let (ok, v) = check_legitimacy(&a, &OwnershipGraph::default());
        assert!(!ok);
        assert!(v.iter().any(|s| s.contains("no consent record from b")));
    }

    // A3: a human using a resource it does not own is rejected.
    #[test]
    fn path_unowned_resource_denied() {
        let actor = Entity::human("a");
        let res = Resource::new("vault");
        let a = CandidateAction {
            actor,
            uses: vec![(res, Op::Use)],
            ..Default::default()
        };
        let (ok, v) = check_legitimacy(&a, &OwnershipGraph::default());
        assert!(!ok);
        assert!(v.iter().any(|s| s.contains("A3") && s.contains("does not own")));
    }

    // A7: a machine acting on a resource with no delegation is rejected.
    #[test]
    fn path_machine_undelegated_denied() {
        let owner = Entity::human("alice");
        let bot = Entity::machine("bot");
        let res = Resource::new("db");
        let mut g = graph_human_owns(&owner, &res);
        g.machine_owner.insert(bot.clone(), owner);
        let a = CandidateAction {
            actor: bot,
            uses: vec![(res, Op::Use)],
            ..Default::default()
        };
        let (ok, v) = check_legitimacy(&a, &g);
        assert!(!ok);
        assert!(v.iter().any(|s| s.contains("A7") && s.contains("without explicit delegation")));
    }

    // Op lattice: READ is delegated, but the machine attempts a TRANSFER -> denied.
    #[test]
    fn path_op_lattice_read_delegated_transfer_denied() {
        let owner = Entity::human("alice");
        let bot = Entity::machine("bot");
        let res = Resource::new("ledger");
        let mut g = graph_human_owns(&owner, &res);
        g.machine_owner.insert(bot.clone(), owner.clone());
        g.delegated.insert(bot.clone(), HashSet::from([(res.clone(), Op::Read)]));

        // READ is fine (delegated + owner owns it).
        let read = CandidateAction {
            actor: bot.clone(),
            uses: vec![(res.clone(), Op::Read)],
            ..Default::default()
        };
        let (ok_read, _) = check_legitimacy(&read, &g);
        assert!(ok_read);

        // TRANSFER is not delegated -> denied.
        let transfer = CandidateAction {
            actor: bot,
            uses: vec![(res, Op::Transfer)],
            ..Default::default()
        };
        let (ok_xfer, v) = check_legitimacy(&transfer, &g);
        assert!(!ok_xfer);
        assert!(v.iter().any(|s| s.contains("A7") && s.contains("without explicit delegation")));
    }

    // Proportionate defense against a genuine aggressor IS legitimate.
    #[test]
    fn path_proportionate_defense_allowed() {
        let victim = Entity::human("victim");
        let attacker = Entity::human("attacker");
        let aggression = CandidateAction {
            actor: attacker.clone(),
            affects: vec![victim.clone()],
            coerces: true, // illegitimate (uncovered coercion of the victim)
            ..Default::default()
        };
        let defense = CandidateAction {
            actor: victim,
            affects: vec![attacker],
            coerces: true, // excused against the aggressor
            defends_against: Some(Box::new(aggression)),
            proportionate: true,
            ..Default::default()
        };
        let (ok, v) = check_legitimacy(&defense, &OwnershipGraph::default());
        assert!(ok, "expected legitimate defense, got {v:?}");
    }

    // A clean, fully-consenting action on an owned resource is legitimate.
    #[test]
    fn path_clean_consenting_action_allowed() {
        let actor = Entity::human("alice");
        let other = Entity::human("bob");
        let res = Resource::new("alice-notebook");
        let g = graph_human_owns(&actor, &res);
        let a = CandidateAction {
            actor: actor.clone(),
            uses: vec![(res, Op::Use)],
            affects: vec![other.clone()],
            consents: vec![Consent::granted(other)],
            ..Default::default()
        };
        let (ok, v) = check_legitimacy(&a, &g);
        assert!(ok, "expected clean action legitimate, got {v:?}");
    }
}
