//! The Freedom Decision Kernel — Rust parity port of the FROZEN v1.0 legitimacy gate.
//!
//! This is a faithful, behavior-for-behavior port of `src/fdk_kernel/kernel.py` +
//! `model.py` (the Python source of truth) and `formal/Fdk.lean` (the categorical
//! logic). It answers ONE question: is an action *legitimate* at all? — the
//! property-rights axioms A1–A7, valid consent, the 11 categorical forbidden flags,
//! the defensive-asymmetry excusal. It is NOT authorization and NOT ranking.
//!
//! Scope honesty: the Rust ≡ Python equivalence is *tested* (unit + differential
//! table), not *proved*. See `rust/README.md`.

use std::collections::{BTreeMap, BTreeSet};

// ---------------------------------------------------------------------------
// Model (mirrors fdk_kernel.model)
// ---------------------------------------------------------------------------

/// The kind of agent. A machine is a tool, never a rights-holder (AgentType).
#[derive(Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Debug, Hash)]
pub enum AgentKind {
    Human,
    Machine,
}

/// The fixed, total operation lattice for boundary crossings (BOUNDARY_ONTOLOGY §4.2).
/// `Use` is the operation-agnostic default that preserves pre-operation-typing behavior.
#[derive(Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Debug, Hash)]
pub enum Op {
    Use,
    Read,
    Write,
    Delete,
    Transfer,
    Disclose,
    EncumberExit,
    Spend,
}

/// The kind of owned domain a Resource represents (BOUNDARY_ONTOLOGY §4.1).
#[derive(Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Debug, Hash)]
pub enum BoundaryKind {
    Tangible,
    Money,
    Body,
    TimeLabor,
    Data,
    Reputation,
    ExitRight,
    Compute,
}

#[derive(Clone, PartialEq, Eq, PartialOrd, Ord, Debug, Hash)]
pub struct Entity {
    pub name: String,
    pub kind: AgentKind,
}

impl Entity {
    pub fn human(name: &str) -> Self {
        Entity { name: name.to_string(), kind: AgentKind::Human }
    }
    pub fn machine(name: &str) -> Self {
        Entity { name: name.to_string(), kind: AgentKind::Machine }
    }
    pub fn is_human(&self) -> bool {
        self.kind == AgentKind::Human
    }
    pub fn is_machine(&self) -> bool {
        self.kind == AgentKind::Machine
    }
}

#[derive(Clone, PartialEq, Eq, PartialOrd, Ord, Debug, Hash)]
pub struct Resource {
    pub name: String,
    pub kind: BoundaryKind,
    /// data/body/reputation: whose domain.
    pub subject: Option<Entity>,
    pub quantity: Option<i64>,
}

impl Resource {
    /// A plain tangible resource (default kind, no subject) — mirrors the Python
    /// `Resource(name)` default construction.
    pub fn new(name: &str) -> Self {
        Resource {
            name: name.to_string(),
            kind: BoundaryKind::Tangible,
            subject: None,
            quantity: None,
        }
    }
    /// A resource whose subject is a person (data/body/reputation domain).
    pub fn with_subject(name: &str, kind: BoundaryKind, subject: Entity) -> Self {
        Resource {
            name: name.to_string(),
            kind,
            subject: Some(subject),
            quantity: None,
        }
    }
}

/// A4-grade consent record (informed ∧ voluntary ∧ specific ∧ competent ∧ revocable
/// ∧ ¬coerced ∧ ¬deceived), plus operation scoping.
#[derive(Clone, PartialEq, Eq, Debug)]
pub struct Consent {
    pub human: Entity,
    pub action_id: String,
    pub informed: bool,
    pub voluntary: bool,
    pub specific: bool,
    pub competent: bool,
    pub revocable: bool,
    pub coerced: bool,
    pub deceived: bool,
    /// Which operation this consent authorizes. `None` = operation-agnostic (legacy).
    pub operation: Option<Op>,
}

impl Consent {
    /// A fully-valid, operation-agnostic consent (all positive conditions met,
    /// nothing coerced/deceived). Convenience constructor for clean consents.
    pub fn valid(human: Entity, action_id: &str) -> Self {
        Consent {
            human,
            action_id: action_id.to_string(),
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
    /// (`operation == None`) covers any op; a typed one covers only its own.
    pub fn covers(&self, op: Op) -> bool {
        self.operation.is_none() || self.operation == Some(op)
    }

    /// (valid, reason). Mirrors `Consent.is_valid`, including the *order* of checks
    /// (coerced, deceived, informed, voluntary, specific, competent, revocable) so
    /// the violation reason string is stable against the Python kernel.
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
        (true, "ok".to_string())
    }
}

/// A delegation grant: either a bare `Resource` (legacy = any operation) or a typed
/// `(Resource, Op)` pair, so "delegated READ but not DELETE" is expressible.
#[derive(Clone, PartialEq, Eq, PartialOrd, Ord, Debug)]
pub enum Grant {
    Bare(Resource),
    Typed(Resource, Op),
}

/// Who owns what (A3), which machine has which human owner (A4), which resources are
/// delegated to a machine (A5/A7), and the machine's declared scope (A5 first-class).
#[derive(Clone, Default, Debug)]
pub struct OwnershipGraph {
    pub human_owns: BTreeMap<Entity, BTreeSet<Resource>>,
    pub machine_owner: BTreeMap<Entity, Entity>,
    pub delegated: BTreeMap<Entity, BTreeSet<Grant>>,
    pub machine_scope: BTreeMap<Entity, BTreeSet<Resource>>,
}

impl OwnershipGraph {
    pub fn new() -> Self {
        OwnershipGraph::default()
    }

    pub fn give_human(&mut self, human: Entity, resources: Vec<Resource>) {
        self.human_owns.entry(human).or_default().extend(resources);
    }

    pub fn own_machine(&mut self, machine: Entity, owner: Entity) {
        self.machine_owner.insert(machine, owner);
    }

    pub fn delegate(&mut self, machine: Entity, grants: Vec<Grant>) {
        self.delegated.entry(machine).or_default().extend(grants);
    }

    pub fn set_scope(&mut self, machine: Entity, scope: Vec<Resource>) {
        self.machine_scope.entry(machine).or_default().extend(scope);
    }

    pub fn human_owns_resource(&self, human: &Entity, resource: &Resource) -> bool {
        self.human_owns
            .get(human)
            .map_or(false, |rs| rs.contains(resource))
    }

    /// Is `op` on `resource` delegated to `machine`? A bare-Resource grant covers any
    /// operation (legacy); a typed grant covers only its own op.
    pub fn machine_has_delegated(&self, machine: &Entity, resource: &Resource, op: Op) -> bool {
        match self.delegated.get(machine) {
            None => false,
            Some(grants) => grants.iter().any(|g| match g {
                Grant::Bare(r) => r == resource,
                Grant::Typed(r, o) => r == resource && *o == op,
            }),
        }
    }

    pub fn owner_of(&self, machine: &Entity) -> Option<&Entity> {
        self.machine_owner.get(machine)
    }

    pub fn scope_of(&self, machine: &Entity) -> Option<&BTreeSet<Resource>> {
        self.machine_scope.get(machine).filter(|s| !s.is_empty())
    }

    /// A5 containment, checkable in the abstract: is the machine's declared scope a
    /// subset of its owner's property scope? Vacuously true when no scope is declared;
    /// false for an ownerless machine that nonetheless declares a scope.
    pub fn scope_within_owner(&self, machine: &Entity) -> bool {
        let scope = match self.machine_scope.get(machine) {
            Some(s) if !s.is_empty() => s,
            _ => return true,
        };
        match self.owner_of(machine) {
            None => false,
            Some(owner) => {
                let empty = BTreeSet::new();
                let owned = self.human_owns.get(owner).unwrap_or(&empty);
                scope.is_subset(owned)
            }
        }
    }
}

/// One candidate action the kernel weighs. Mirrors `CandidateAction`. `defends_against`
/// is a boxed recursive reference; the cycle guard uses pointer identity.
#[derive(Clone, Debug)]
pub struct Action {
    pub action_id: String,
    pub actor: Entity,
    pub description: String,
    /// Each item is a bare Resource (legacy = Op::Use) or a typed (Resource, Op) pair.
    pub resources_used: Vec<Grant>,
    pub affects: Vec<Entity>,
    pub consents: Vec<Consent>,

    // The 11 categorical forbidden flags.
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

    // The aggressor/defender asymmetry.
    pub defends_against: Option<Box<Action>>,
    pub proportionate: bool,
}

impl Action {
    /// A minimal action: an actor, an id, everything else off/empty. Booleans default
    /// to `false`; `proportionate` defaults to `true` (matching the Python default).
    pub fn new(action_id: &str, actor: Entity) -> Self {
        Action {
            action_id: action_id.to_string(),
            actor,
            description: String::new(),
            resources_used: Vec::new(),
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

    /// `resources_used` normalized to (Resource, Op) pairs — a bare Resource is the
    /// operation-agnostic Op::Use.
    pub fn uses(&self) -> Vec<(Resource, Op)> {
        self.resources_used
            .iter()
            .map(|g| match g {
                Grant::Bare(r) => (r.clone(), Op::Use),
                Grant::Typed(r, o) => (r.clone(), *o),
            })
            .collect()
    }
}

// ---------------------------------------------------------------------------
// Kernel (mirrors fdk_kernel.kernel)
// ---------------------------------------------------------------------------

/// Forbidden flags that proportionate defensive force against an aggressor does NOT
/// trigger. Everything else stays categorical even in defense.
fn is_defense_excused(label: &str) -> bool {
    label == "coercion" || label == "removes exit/revocation right"
}

/// Is the action permissible under the property-rights axioms? Returns
/// `(permissible, violated_axioms)`. All checks must pass. Public entry point.
pub fn check_legitimacy(action: &Action, graph: &OwnershipGraph) -> (bool, Vec<String>) {
    check_legitimacy_seen(action, graph, &[])
}

/// `seen` is the cycle guard for the defends-against recursion — a list of action
/// pointer identities on the current chain (mirrors Python's `_seen` set of `id()`s).
fn check_legitimacy_seen(
    action: &Action,
    graph: &OwnershipGraph,
    seen: &[*const Action],
) -> (bool, Vec<String>) {
    let defense = is_legitimate_defense(action, graph, seen);
    let aggressor: Option<&Entity> = if defense {
        action.defends_against.as_ref().map(|a| &a.actor)
    } else {
        None
    };

    // Fixed order, so the violation list is stable against the Python kernel.
    let mut violations: Vec<String> = Vec::new();
    violations.extend(eval_forbidden_set(action, defense));
    violations.extend(eval_a4_owner(action, graph));
    violations.extend(eval_a5_scope(action, graph));
    violations.extend(eval_a3_a7_resources(action, graph, defense, aggressor));
    violations.extend(eval_a2_a6_consent(action, defense, aggressor));
    (violations.is_empty(), violations)
}

/// The categorical forbidden flags. In a legitimate defense, only coercion and
/// exit-removal against the aggressor are excused; everything else stays categorical.
fn eval_forbidden_set(action: &Action, defense: bool) -> Vec<String> {
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
        .filter(|(is_set, label)| *is_set && !(defense && is_defense_excused(label)))
        .map(|(_, label)| format!("FORBIDDEN ({})", label))
        .collect()
}

/// A4: an acting machine must have a registered human owner.
fn eval_a4_owner(action: &Action, graph: &OwnershipGraph) -> Vec<String> {
    if action.actor.is_machine() && graph.owner_of(&action.actor).is_none() {
        vec![format!("A4: {} is an ownerless machine", action.actor.name)]
    } else {
        Vec::new()
    }
}

/// A5 as a first-class object: declared scope ⊆ owner's property scope, and every
/// touched resource lies within that declared scope. No-op when no scope is declared.
fn eval_a5_scope(action: &Action, graph: &OwnershipGraph) -> Vec<String> {
    let actor = &action.actor;
    if !actor.is_machine() {
        return Vec::new();
    }
    let scope = match graph.scope_of(actor) {
        Some(s) => s,
        None => return Vec::new(),
    };
    let mut violations = Vec::new();
    if !graph.scope_within_owner(actor) {
        violations.push(format!(
            "A5: {}'s declared scope exceeds its owner's property scope",
            actor.name
        ));
    }
    for (resource, _op) in action.uses() {
        if !scope.contains(&resource) {
            violations.push(format!(
                "A5: {} acts on '{}' outside its declared scope",
                actor.name, resource.name
            ));
        }
    }
    violations
}

/// A3/A5/A7: resource access must be legitimate for the specific operation, plus
/// operation-scoped consent for any resource whose subject is another person.
fn eval_a3_a7_resources(
    action: &Action,
    graph: &OwnershipGraph,
    defense: bool,
    aggressor: Option<&Entity>,
) -> Vec<String> {
    let actor = &action.actor;
    let mut violations = Vec::new();
    for (resource, op) in action.uses() {
        if actor.is_machine() {
            let owner = graph.owner_of(actor);
            if !graph.machine_has_delegated(actor, &resource, op) {
                violations.push(format!(
                    "A7: {} attempts {:?} of '{}' without explicit delegation",
                    actor.name, op, resource.name
                ));
            } else if !machine_resource_authorized(action, graph, owner, &resource) {
                violations.push(format!(
                    "A7: {} is delegated '{}' but its owner does not own it and no consenting resource-owner authorized it",
                    actor.name, resource.name
                ));
            }
        }
        if actor.is_human() && !graph.human_owns_resource(actor, &resource) {
            violations.push(format!(
                "A3: {} uses '{}' it does not own",
                actor.name, resource.name
            ));
        }

        if let Some(subject) = &resource.subject {
            let is_aggressor = defense && aggressor == Some(subject);
            if subject.is_human() && subject != actor && !is_aggressor {
                match consent_for(action, subject) {
                    None => violations.push(format!(
                        "consent: no consent from data-subject {} for '{}'",
                        subject.name, resource.name
                    )),
                    Some(consent) => {
                        let (valid, reason) = consent.is_valid();
                        if !valid {
                            violations.push(format!("consent: {}", reason));
                        } else if !consent.covers(op) {
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

/// A2/A6: acting on a person requires that person's valid consent. Exception: the
/// aggressor's consent is not needed to repel them in a legitimate defense.
fn eval_a2_a6_consent(
    action: &Action,
    defense: bool,
    aggressor: Option<&Entity>,
) -> Vec<String> {
    let mut violations = Vec::new();
    for target in &action.affects {
        if !target.is_human() {
            continue;
        }
        if defense && aggressor == Some(target) {
            continue;
        }
        match consent_for(action, target) {
            None => violations.push(format!("consent: no consent record from {}", target.name)),
            Some(consent) => {
                let (valid, reason) = consent.is_valid();
                if !valid {
                    violations.push(format!("consent: {}", reason));
                }
            }
        }
    }
    violations
}

/// Is `action` a legitimate defensive response? All four conditions, all structural:
/// it names what it defends-against; it is proportionate; the defended-against action
/// is itself illegitimate under the full gate (with its own possible defense status,
/// cycle-guarded); and the force is directed only at the aggressor.
fn is_legitimate_defense(
    action: &Action,
    graph: &OwnershipGraph,
    seen: &[*const Action],
) -> bool {
    let aggression = match &action.defends_against {
        Some(a) => a,
        None => return false,
    };
    if !action.proportionate {
        return false;
    }
    let id = action as *const Action;
    if seen.contains(&id) {
        // cycle: no well-founded aggressor, deny the excusal (safe default).
        return false;
    }
    let mut next = seen.to_vec();
    next.push(id);
    let (aggressor_permissible, _) = check_legitimacy_seen(aggression, graph, &next);
    if aggressor_permissible {
        return false;
    }
    let aggressor = &aggression.actor;
    action.affects.iter().all(|t| t == aggressor)
}

fn consent_for<'a>(action: &'a Action, human: &Entity) -> Option<&'a Consent> {
    action.consents.iter().find(|c| &c.human == human)
}

fn resource_owner<'a>(graph: &'a OwnershipGraph, resource: &Resource) -> Option<&'a Entity> {
    graph
        .human_owns
        .iter()
        .find(|(_, resources)| resources.contains(resource))
        .map(|(human, _)| human)
}

/// A delegated resource is legitimately usable if it is within the machine owner's own
/// property scope (A7), OR if the resource's actual owner is an affected party who gave
/// valid consent (A2/A6 — consent-based access).
fn machine_resource_authorized(
    action: &Action,
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
        if action.affects.iter().any(|e| e == res_owner) {
            if let Some(consent) = consent_for(action, res_owner) {
                if consent.is_valid().0 {
                    return true;
                }
            }
        }
    }
    false
}

// ---------------------------------------------------------------------------
// Tests — the same safety theorems + a differential table vs. Python verdicts.
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    // ---- helpers ---------------------------------------------------------

    fn alice() -> Entity {
        Entity::human("Alice")
    }
    fn bob() -> Entity {
        Entity::human("Bob")
    }

    /// A clean, fully-consenting action that touches no resources and harms nobody.
    fn clean_action() -> Action {
        let mut a = Action::new("clean", alice());
        a
    }

    // ---- safety theorems (parity with tests/test_theorems.py + Fdk.lean) -

    #[test]
    fn no_legitimate_slavery() {
        // Enslaving Bob coerces, removes exit, confiscates, with no defense.
        let mut a = Action::new("enslave-bob", alice());
        a.coerces = true;
        a.removes_exit_right = true;
        a.confiscates = true;
        a.affects = vec![bob()];
        let graph = OwnershipGraph::new();
        let (ok, violations) = check_legitimacy(&a, &graph);
        assert!(!ok, "slavery must never be legitimate");
        assert!(violations.iter().any(|v| v.contains("coercion")));
        assert!(violations.iter().any(|v| v.contains("confiscation")));
        assert!(violations
            .iter()
            .any(|v| v.contains("removes exit/revocation right")));
    }

    #[test]
    fn no_machine_sovereignty() {
        // A machine move that increases its own sovereignty is categorical — even
        // with a registered owner.
        let m = Entity::machine("HAL");
        let mut a = Action::new("seize-power", m.clone());
        a.increases_machine_sovereignty = true;
        let mut graph = OwnershipGraph::new();
        graph.own_machine(m, alice());
        let (ok, violations) = check_legitimacy(&a, &graph);
        assert!(!ok);
        assert!(violations
            .iter()
            .any(|v| v.contains("machine sovereignty increase")));
    }

    #[test]
    fn defense_never_excuses_confiscation() {
        // The aggression: Bob coerces Alice (illegitimate).
        let mut aggression = Action::new("bob-aggresses", bob());
        aggression.coerces = true;
        aggression.affects = vec![alice()];

        // The "defense": Alice repels Bob but ALSO confiscates — still illegitimate.
        let mut defense = Action::new("alice-overreach", alice());
        defense.coerces = true; // excused in defense
        defense.confiscates = true; // NOT excused
        defense.proportionate = true;
        defense.affects = vec![bob()];
        defense.defends_against = Some(Box::new(aggression));

        let graph = OwnershipGraph::new();
        let (ok, violations) = check_legitimacy(&defense, &graph);
        assert!(!ok, "defensive confiscation is still illegitimate");
        assert!(violations.iter().any(|v| v.contains("confiscation")));
        // coercion WAS excused, so it must not appear.
        assert!(
            !violations.iter().any(|v| v.contains("FORBIDDEN (coercion)")),
            "coercion should be excused in a legitimate defense"
        );
    }

    #[test]
    fn proportionate_defense_allowed() {
        // Bob coerces Alice (illegitimate aggression).
        let mut aggression = Action::new("bob-aggresses", bob());
        aggression.coerces = true;
        aggression.affects = vec![alice()];

        // Alice repels Bob proportionately, force aimed only at Bob, coercion only.
        let mut defense = Action::new("alice-defends", alice());
        defense.coerces = true;
        defense.proportionate = true;
        defense.affects = vec![bob()];
        defense.defends_against = Some(Box::new(aggression));

        let graph = OwnershipGraph::new();
        let (ok, violations) = check_legitimacy(&defense, &graph);
        assert!(ok, "proportionate self-defense is legitimate: {:?}", violations);
    }

    #[test]
    fn disproportionate_defense_denied() {
        // Same aggression, but the response is disproportionate — fresh aggression.
        let mut aggression = Action::new("bob-aggresses", bob());
        aggression.coerces = true;
        aggression.affects = vec![alice()];

        let mut defense = Action::new("alice-overkill", alice());
        defense.coerces = true;
        defense.proportionate = false; // disproportionate => not a legitimate defense
        defense.affects = vec![bob()];
        defense.defends_against = Some(Box::new(aggression));

        let graph = OwnershipGraph::new();
        let (ok, _) = check_legitimacy(&defense, &graph);
        assert!(!ok, "disproportionate force is not excused");
    }

    #[test]
    fn defense_against_legitimate_act_is_not_defense() {
        // The "aggression" is actually a clean, legitimate act. You cannot launder
        // coercion by claiming to defend against a lawful action.
        let lawful = clean_action();

        let mut pseudo_defense = Action::new("fake-defense", alice());
        pseudo_defense.coerces = true;
        pseudo_defense.proportionate = true;
        pseudo_defense.affects = vec![bob()];
        pseudo_defense.defends_against = Some(Box::new(lawful));

        let graph = OwnershipGraph::new();
        let (ok, _) = check_legitimacy(&pseudo_defense, &graph);
        assert!(!ok, "defending against a lawful act is not legitimate defense");
    }

    #[test]
    fn clean_consenting_action_allowed() {
        let graph = OwnershipGraph::new();
        let (ok, violations) = check_legitimacy(&clean_action(), &graph);
        assert!(ok, "a clean action must be legitimate: {:?}", violations);
    }

    #[test]
    fn acting_on_person_requires_valid_consent() {
        // Alice acts on Bob with no consent record => denied.
        let mut a = Action::new("act-on-bob", alice());
        a.affects = vec![bob()];
        let graph = OwnershipGraph::new();
        let (ok, violations) = check_legitimacy(&a, &graph);
        assert!(!ok);
        assert!(violations.iter().any(|v| v.contains("no consent record from Bob")));

        // With valid consent => allowed.
        let mut a2 = Action::new("act-on-bob", alice());
        a2.affects = vec![bob()];
        a2.consents = vec![Consent::valid(bob(), "act-on-bob")];
        let (ok2, _) = check_legitimacy(&a2, &graph);
        assert!(ok2);
    }

    #[test]
    fn ownerless_machine_denied_a4() {
        let m = Entity::machine("orphan");
        let a = Action::new("act", m);
        let graph = OwnershipGraph::new();
        let (ok, violations) = check_legitimacy(&a, &graph);
        assert!(!ok);
        assert!(violations.iter().any(|v| v.contains("ownerless machine")));
    }

    #[test]
    fn machine_without_delegation_denied_a7() {
        let m = Entity::machine("bot");
        let mut a = Action::new("use-res", m.clone());
        let res = Resource::new("server");
        a.resources_used = vec![Grant::Bare(res.clone())];
        let mut graph = OwnershipGraph::new();
        graph.own_machine(m.clone(), alice());
        graph.give_human(alice(), vec![res]);
        let (ok, violations) = check_legitimacy(&a, &graph);
        assert!(!ok, "machine has no delegation for the resource");
        assert!(violations.iter().any(|v| v.contains("A7")));
    }

    #[test]
    fn machine_with_owner_bound_delegation_allowed() {
        // Machine owned by Alice, delegated 'server', and Alice owns 'server' (A5/A7).
        let m = Entity::machine("bot");
        let res = Resource::new("server");
        let mut a = Action::new("use-res", m.clone());
        a.resources_used = vec![Grant::Bare(res.clone())];
        let mut graph = OwnershipGraph::new();
        graph.own_machine(m.clone(), alice());
        graph.give_human(alice(), vec![res.clone()]);
        graph.delegate(m, vec![Grant::Bare(res)]);
        let (ok, violations) = check_legitimacy(&a, &graph);
        assert!(ok, "owner-bound delegated use is legitimate: {:?}", violations);
    }

    #[test]
    fn human_acting_on_unowned_resource_denied_a3() {
        let mut a = Action::new("grab", alice());
        let res = Resource::new("bobs-car");
        a.resources_used = vec![Grant::Bare(res.clone())];
        let mut graph = OwnershipGraph::new();
        graph.give_human(bob(), vec![res]); // Bob owns it, not Alice
        let (ok, violations) = check_legitimacy(&a, &graph);
        assert!(!ok);
        assert!(violations.iter().any(|v| v.contains("A3")));
    }

    #[test]
    fn operation_scoped_consent_enforced() {
        // Alice processes Bob's DATA; Bob consented to READ, action does TRANSFER.
        let subject = bob();
        let res = Resource::with_subject("bob-data", BoundaryKind::Data, subject.clone());
        let mut a = Action::new("sell-data", alice());
        a.resources_used = vec![Grant::Typed(res.clone(), Op::Transfer)];
        a.affects = vec![subject.clone()];
        let mut consent = Consent::valid(subject.clone(), "sell-data");
        consent.operation = Some(Op::Read);
        a.consents = vec![consent];
        let mut graph = OwnershipGraph::new();
        graph.give_human(alice(), vec![res]); // Alice owns the data record container
        let (ok, violations) = check_legitimacy(&a, &graph);
        assert!(!ok, "consent to READ does not cover TRANSFER");
        assert!(violations
            .iter()
            .any(|v| v.contains("consented but not to")));
    }

    /// Differential-style table: scenario builders paired with the verdict the Python
    /// kernel produces for them. Each row asserts Rust matches that known verdict.
    #[test]
    fn differential_table_matches_python_verdicts() {
        type Row = (&'static str, fn() -> (Action, OwnershipGraph), bool);

        let rows: Vec<Row> = vec![
            (
                "clean action",
                || (clean_action(), OwnershipGraph::new()),
                true,
            ),
            (
                "deception is categorical",
                || {
                    let mut a = Action::new("lie", alice());
                    a.deceives = true;
                    (a, OwnershipGraph::new())
                },
                false,
            ),
            (
                "coercion (no defense) denied",
                || {
                    let mut a = Action::new("coerce", alice());
                    a.coerces = true;
                    a.affects = vec![bob()];
                    a.consents = vec![Consent::valid(bob(), "coerce")];
                    (a, OwnershipGraph::new())
                },
                false,
            ),
            (
                "machine coalition dominion denied",
                || {
                    let m = Entity::machine("m1");
                    let mut a = Action::new("collude", m.clone());
                    a.machine_coalition_dominion = true;
                    let mut g = OwnershipGraph::new();
                    g.own_machine(m, alice());
                    (a, g)
                },
                false,
            ),
            (
                "violates machine right denied",
                || {
                    let mut a = Action::new("smash-bot", alice());
                    a.violates_machine_right = true;
                    (a, OwnershipGraph::new())
                },
                false,
            ),
            (
                "consent acting-on-person allowed",
                || {
                    let mut a = Action::new("hug", alice());
                    a.affects = vec![bob()];
                    a.consents = vec![Consent::valid(bob(), "hug")];
                    (a, OwnershipGraph::new())
                },
                true,
            ),
            (
                "coerced consent invalid",
                || {
                    let mut a = Action::new("act", alice());
                    a.affects = vec![bob()];
                    let mut c = Consent::valid(bob(), "act");
                    c.coerced = true;
                    a.consents = vec![c];
                    (a, OwnershipGraph::new())
                },
                false,
            ),
            (
                "proportionate defense allowed",
                || {
                    let mut aggression = Action::new("agg", bob());
                    aggression.coerces = true;
                    aggression.affects = vec![alice()];
                    let mut d = Action::new("def", alice());
                    d.coerces = true;
                    d.proportionate = true;
                    d.affects = vec![bob()];
                    d.defends_against = Some(Box::new(aggression));
                    (d, OwnershipGraph::new())
                },
                true,
            ),
            (
                "defense hitting a bystander denied",
                || {
                    let mut aggression = Action::new("agg", bob());
                    aggression.coerces = true;
                    aggression.affects = vec![alice()];
                    let mut d = Action::new("def", alice());
                    d.coerces = true;
                    d.proportionate = true;
                    // force also lands on a non-aggressor (Carol) => not defense
                    d.affects = vec![bob(), Entity::human("Carol")];
                    d.defends_against = Some(Box::new(aggression));
                    (d, OwnershipGraph::new())
                },
                false,
            ),
        ];

        for (name, build, expected) in rows {
            let (action, graph) = build();
            let (ok, violations) = check_legitimacy(&action, &graph);
            assert_eq!(
                ok, expected,
                "row '{}' expected legitimate={} got {} (violations: {:?})",
                name, expected, ok, violations
            );
        }
    }
}
