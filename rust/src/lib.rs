//! FDK — Rust parity port of the FROZEN v1.0 legitimacy kernel (categorical core).
//!
//! Mirrors `formal/Fdk.lean` and `src/fdk_kernel/kernel.py`: the 11 categorical
//! forbidden flags, the defensive-asymmetry excusal of coercion/exit-removal, and the
//! valid-consent gate. Honest scope: this is a *parity port* of the categorical core
//! (consent/ownership are abstracted into one `valid_consent` boolean, exactly as in
//! the Lean model). Rust <-> Python equivalence is **tested** via the shared safety
//! theorems, not proved. The frozen surface (`spec/FREEZE.md`) is matched.
//!
//! Build (NON-ASCII repo path workaround): `CARGO_TARGET_DIR=C:/fdkrust cargo test`.

#![forbid(unsafe_code)]

/// A human is a rights-holder; a machine is a tool with a human owner.
#[derive(Clone, Copy, PartialEq, Eq, Debug, Default)]
pub enum AgentKind {
    #[default]
    Human,
    Machine,
}

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

#[cfg(test)]
mod tests {
    use super::*;

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
        // (action, expected legitimate?)
        let deception = Action { deceives: true, valid_consent: true, ..Default::default() };
        assert!(!legitimate(&deception));
        let coalition = Action {
            machine_coalition_dominion: true, valid_consent: true, ..Default::default()
        };
        assert!(!legitimate(&coalition));
        // coercion alone, NOT a defense -> denied
        let coerce = Action { coerces: true, valid_consent: true, ..Default::default() };
        assert!(!legitimate(&coerce));
    }
}
