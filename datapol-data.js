window.DATAPOL_SYNC_DATA = {
  "metadata": {
    "syncedAt": "2026-03-15T00:09:47.133078+00:00",
    "source": "web-risk-database.json",
    "recordCount": 8
  },
  "risks": [
    {
      "id": "WEB-TMG-001",
      "catID": "TMG",
      "hazard": "Queue-End Rear-End Collision in Work Zone Approach",
      "mechanism": "Insufficient advance warning and speed harmonization causes late braking into stopped queues.",
      "impact": "High-energy multi-vehicle crash near the work zone.",
      "initialLikelihood": "Likely (4)",
      "initialConsequence": "Major (4)",
      "residualLikelihood": "Unlikely (2)",
      "residualConsequence": "Moderate (3)",
      "riskOwner": "Traffic Engineer",
      "action": "Implement queue detection triggers and dynamic warning treatment on approaches.",
      "reference": "FHWA Work Zone Management Program; MUTCD 6C",
      "mitigations": [
        "Add upstream queue warning and variable message boards based on observed queue length.",
        "Re-check taper length and warning sign spacing against operating speed.",
        "Adjust staging windows to avoid peak-period queue growth where practical."
      ],
      "evidenceSignals": [
        "advance warning",
        "transition area",
        "queue",
        "mobility"
      ],
      "submittedBy": "Web Risk Analyzer",
      "submittedAt": "2026-03-15T00:09:47.131667+00:00",
      "source": "web-analysis"
    },
    {
      "id": "WEB-TMG-002",
      "catID": "TMG",
      "hazard": "Pedestrian Detour Non-Compliance and DDA Conflict",
      "mechanism": "Temporary footpath/crossing arrangement lacks continuity, detectable edging, or accessible routing.",
      "impact": "Pedestrians enter live traffic space or trip/fall through non-compliant detours.",
      "initialLikelihood": "Possible (3)",
      "initialConsequence": "Major (4)",
      "residualLikelihood": "Rare (1)",
      "residualConsequence": "Moderate (3)",
      "riskOwner": "Site Supervisor",
      "action": "Approve and monitor pedestrian detours daily with accessibility checks.",
      "reference": "MUTCD 6D and 6F.74",
      "mitigations": [
        "Provide continuous protected pedestrian pathways with compliant surface and width.",
        "Install detectable edging and clear detour wayfinding at each closure point.",
        "Inspect detour condition after weather and shift changes."
      ],
      "evidenceSignals": [
        "pedestrian",
        "accessibility",
        "crosswalk",
        "detectable edging"
      ],
      "submittedBy": "Web Risk Analyzer",
      "submittedAt": "2026-03-15T00:09:47.131667+00:00",
      "source": "web-analysis"
    },
    {
      "id": "WEB-TMG-003",
      "catID": "TMG",
      "hazard": "Live-lane Worker Struck-By Due to Intrusion",
      "mechanism": "Passing traffic or site vehicles enter the activity area because separation and warning controls are insufficient.",
      "impact": "Severe worker injury/fatality and immediate site shutdown.",
      "initialLikelihood": "Likely (4)",
      "initialConsequence": "Catastrophic (5)",
      "residualLikelihood": "Unlikely (2)",
      "residualConsequence": "Major (4)",
      "riskOwner": "Traffic Control Supervisor",
      "action": "Strengthen positive protection, buffer controls, and intrusion response procedures before shift start.",
      "reference": "OSHA Highway Work Zones; MUTCD Part 6D",
      "mitigations": [
        "Install positive protection and maintain compliant lateral offsets in active work areas.",
        "Deploy shadow vehicles/TMA where exposure to live traffic exists.",
        "Brief crews on emergency intrusion response and safe refuge points each shift."
      ],
      "evidenceSignals": [
        "struck-by",
        "worker safety",
        "activity area"
      ],
      "submittedBy": "Web Risk Analyzer",
      "submittedAt": "2026-03-15T00:09:47.131667+00:00",
      "source": "web-analysis"
    },
    {
      "id": "WEB-ETT-001",
      "catID": "ETT",
      "hazard": "Incorrect Taper Length for Posted Speed",
      "mechanism": "Temporary taper geometry is undersized for approach speed and does not provide sufficient merge distance.",
      "impact": "Abrupt lane changes, side-swipes, and loss-of-control events at merge points.",
      "initialLikelihood": "Possible (3)",
      "initialConsequence": "Major (4)",
      "residualLikelihood": "Rare (1)",
      "residualConsequence": "Moderate (3)",
      "riskOwner": "Design Engineer",
      "action": "Recalculate taper geometry against current speed environment before deployment.",
      "reference": "MUTCD Table 6C-3 and 6C-4",
      "mitigations": [
        "Verify taper calculations and field lengths against current speed and lane width.",
        "Update traffic control diagrams when speed environment or lane configuration changes.",
        "Use independent verification sign-off before opening altered staging."
      ],
      "evidenceSignals": [
        "taper",
        "table 6c-3",
        "speed"
      ],
      "submittedBy": "Web Risk Analyzer",
      "submittedAt": "2026-03-15T00:09:47.131667+00:00",
      "source": "web-analysis"
    },
    {
      "id": "WEB-TMG-004",
      "catID": "TMG",
      "hazard": "Flagger Visibility and Positioning Failure",
      "mechanism": "Flagger station placement and conspicuity do not provide adequate sight distance for approaching drivers.",
      "impact": "Delayed driver compliance, unsafe stop maneuvers, and worker exposure.",
      "initialLikelihood": "Possible (3)",
      "initialConsequence": "Major (4)",
      "residualLikelihood": "Rare (1)",
      "residualConsequence": "Moderate (3)",
      "riskOwner": "Traffic Control Supervisor",
      "action": "Audit flagger station placement each shift and enforce high-visibility apparel requirements.",
      "reference": "MUTCD Chapter 6E; OSHA Highway Work Zones",
      "mitigations": [
        "Position flagger stations to preserve stopping sight distance and clear escape routes.",
        "Use compliant STOP/SLOW devices and high-visibility PPE for all flaggers.",
        "Apply radio protocol checks for handover periods and low-light operations."
      ],
      "evidenceSignals": [
        "flagger",
        "high-visibility",
        "sight distance"
      ],
      "submittedBy": "Web Risk Analyzer",
      "submittedAt": "2026-03-15T00:09:47.131667+00:00",
      "source": "web-analysis"
    },
    {
      "id": "WEB-BDR-001",
      "catID": "BDR",
      "hazard": "Temporary Barrier Gap at Transition or Terminal",
      "mechanism": "Mismatch or discontinuity at temporary barrier transitions creates a non-redirective snag point.",
      "impact": "Vehicle penetration or severe redirection failure into workers/hazards.",
      "initialLikelihood": "Possible (3)",
      "initialConsequence": "Catastrophic (5)",
      "residualLikelihood": "Unlikely (2)",
      "residualConsequence": "Major (4)",
      "riskOwner": "Barrier Designer",
      "action": "Verify transition compatibility and terminal details during install hold-point inspections.",
      "reference": "MUTCD 6F.85 Temporary Traffic Barriers; FHWA Work Zones",
      "mitigations": [
        "Inspect every transition and end treatment against manufacturer and project requirements.",
        "Replace damaged or non-compatible transition components before opening to traffic.",
        "Confirm working width and barrier alignment with surveyed setout checks."
      ],
      "evidenceSignals": [
        "temporary traffic barriers",
        "crash cushions"
      ],
      "submittedBy": "Web Risk Analyzer",
      "submittedAt": "2026-03-15T00:09:47.131667+00:00",
      "source": "web-analysis"
    },
    {
      "id": "WEB-TMG-005",
      "catID": "TMG",
      "hazard": "Portable Device Failure (PCMS/Arrow Board) During Stage",
      "mechanism": "Power loss, misconfiguration, or poor placement of temporary warning devices reduces driver guidance.",
      "impact": "Driver confusion, late merges, and elevated side-swipe/rear-end crash potential.",
      "initialLikelihood": "Possible (3)",
      "initialConsequence": "Major (4)",
      "residualLikelihood": "Rare (1)",
      "residualConsequence": "Moderate (3)",
      "riskOwner": "Traffic Control Supervisor",
      "action": "Add pre-open functionality checks and redundancy for all portable warning devices.",
      "reference": "MUTCD 6F.60 and 6F.61",
      "mitigations": [
        "Run pre-start checks for visibility, battery/solar status, and message accuracy.",
        "Position devices to meet approach visibility and lane guidance requirements.",
        "Maintain spare devices for rapid replacement during active shifts."
      ],
      "evidenceSignals": [
        "portable changeable message signs",
        "arrow boards"
      ],
      "submittedBy": "Web Risk Analyzer",
      "submittedAt": "2026-03-15T00:09:47.131667+00:00",
      "source": "web-analysis"
    },
    {
      "id": "WEB-BDR-002",
      "catID": "BDR",
      "hazard": "Crash Cushion Not Restored After Impact",
      "mechanism": "Impact attenuator remains in compromised condition after strike, reducing energy absorption performance.",
      "impact": "Increased crash severity for subsequent impacts.",
      "initialLikelihood": "Possible (3)",
      "initialConsequence": "Major (4)",
      "residualLikelihood": "Rare (1)",
      "residualConsequence": "Moderate (3)",
      "riskOwner": "Maintenance Lead",
      "action": "Set maximum response times and inspection logs for impact device reset/replacement.",
      "reference": "MUTCD 6F.86 Crash Cushions",
      "mitigations": [
        "Inspect all cushions after reported or suspected impact events.",
        "Quarantine damaged units and replace cartridges/modules before reopening lanes.",
        "Track repair turnaround and escalate overdue resets to site leadership."
      ],
      "evidenceSignals": [
        "crash cushions"
      ],
      "submittedBy": "Web Risk Analyzer",
      "submittedAt": "2026-03-15T00:09:47.131667+00:00",
      "source": "web-analysis"
    }
  ]
};
