# Missing Study Triage

This document prioritizes workbook-listed studies that are absent from the checked-in student extraction and are most likely to yield ROI-level effect information after paper review.

## Scope

- Source workbook: `C:\Users\dpado\Documents\jhu\Oto-HNS\meta_analysis\meta_analysis_vestibular_gm_wm.xlsx`
- Current checked-in study table: `scientific_grouping_decisions.csv`
- Workbook taxonomy crosswalk: `workbook_review_frame_crosswalk.csv`

## Summary

- Missing workbook studies triaged: 50
- High priority: 31
- Medium priority: 15
- Low priority: 4
- Ready for manual review: 41
- Hold for author-year collision: 1
- Hold for scope split: 7
- Hold for both issues: 1
- Workbook study labels normalized: 6

## Dedup And Scope Audit

- `ready_for_manual_review` means the workbook row does not show an author-year collision or obvious mixed-scope problem in this triage pass.
- `hold_author_year_collision` means another missing row shares the same normalized author-year signature, so same-paper versus companion-paper status should be resolved before review.
- `hold_scope_split` means the workbook row mixes multiple conditions or design frames and should be split before review.
- `hold_author_year_collision_and_scope_split` means both warnings apply and the row should stay out of the primary review queue.

### Hold List

- `Conrad et al., 2022` | `Infarcts of the subcortical vestibular circuitry` | `hold_author_year_collision`
  Note: Workbook study label normalized for year or punctuation noise. Another missing-study row shares this author-year signature; resolve same-year paper versus duplicate before extraction.
- `Fettrow et al., 2023` | `Healthy younger & older adults; Healthy younger vs. older adults` | `hold_scope_split`
  Note: Workbook entry mixes multiple conditions, frames, or cohort types and should be split or scoped before review.
- `Hummel et al., 2014` | `Bilateral vestibulopathy (BVP), "Vestibular Experts"` | `hold_scope_split`
  Note: Workbook entry mixes multiple conditions, frames, or cohort types and should be split or scoped before review.
- `Hupfeld et al., 2022` | `Healthy younger & older adults; Healthy younger vs. older adults; Long‐duration spaceflight (astronauts)` | `hold_scope_split`
  Note: Workbook entry mixes multiple conditions, frames, or cohort types and should be split or scoped before review.
- `McGregor et al., 2023` | `Long‐duration spaceflight (astronauts); Varied duration spaceflight (astronauts)` | `hold_scope_split`
  Note: Workbook entry mixes multiple conditions, frames, or cohort types and should be split or scoped before review.
- `Hadi et al., 2022` | `Healthy + lesion or normal variants` | `hold_scope_split`
  Note: Workbook study label normalized for year or punctuation noise. Workbook entry mixes multiple conditions, frames, or cohort types and should be split or scoped before review.
- `Ibitoye et al., 2023` | `Review or combined study on “OP2” region` | `hold_scope_split`
  Note: Workbook entry mixes multiple conditions, frames, or cohort types and should be split or scoped before review.
- `Oussoren et al., 2022` | `Vestibular neuritis + cerebral small vessel disease` | `hold_scope_split`
  Note: Workbook entry mixes multiple conditions, frames, or cohort types and should be split or scoped before review.
- `Conrad et al., 2022` | `Unilateral subcortical or infratentorial ischemic stroke; Unilateral thalamic or brainstem infarction` | `hold_author_year_collision_and_scope_split`
  Note: Another missing-study row shares this author-year signature; resolve same-year paper versus duplicate before extraction. Workbook entry mixes multiple conditions, frames, or cohort types and should be split or scoped before review.

## Reading Strategy

- Start with the `ready_for_manual_review` subset of the high-priority group. Those are the cleanest candidates for ROI-wise extraction with convertible statistics.
- Use the medium-priority group only after the clean high-priority queue is exhausted or if those studies target especially important review bins.
- Resolve all hold-list rows before manual review so the extraction queue does not start with duplicate-risk or mixed-scope studies.
- Defer the low-priority group unless you broaden the table schema beyond ROI-level effect-size extraction.

## High Priority

- `Calzolari et al., 2021` | `Traumatic Brain Injury (TBI) with vestibular agnosia` | `Post-traumatic or concussive vestibulopathy` | `ready_for_manual_review`
  Rationale: Workbook notes suggest explicit regions, quantitative imaging metrics, and a usable comparison design.
  Dedup/scope note: Workbook study label normalized for year or punctuation noise.
  Region summary: corpus callosum (bilateral, genu, body, splenium), fornix (bilateral, column, body, cres),internal capsule (bilateral, anterior limb, posterior limb, retrolenticular part), corona radiata (bilateral, anterior, superior, posterior), cerebral peduncle (bilateral), anterior thalamic radiation (bilateral), posterior thalamic radiation (right), sagittal stratum (bilateral), external capsule (bilateral), superior longitudinal fasciculus (bilateral), inferior longitudinal fasciculus (bilateral), superior fronto-occipital fasciculus (right), uncinate fasciculus (bilateral), cingulum (bilateral, cingulate gyrus), fornix (bilateral, column, body), fornix/stria terminalis (bilateral), tapetum (bilateral)
- `Conrad et al., 2021` | `Cerebellar infarction` | `Stroke or ischemic vestibular-circuit lesions` | `ready_for_manual_review`
  Rationale: Workbook notes suggest explicit regions, quantitative imaging metrics, and a usable comparison design.
  Dedup/scope note: No duplicate or scope warning detected in the workbook triage pass.
  Region summary: Cerebellum (bilateral, crus I, crus II, lobule VI, lobule VIII, lobule IX, lobule X), premotor cortex (bilateral, corticospinal tract), corpus callosum (bilateral, genu, body), dorsolateral prefrontal cortex (bilateral), ventrolateral prefrontal cortex (bilateral), precentral gyrus (left, area 4), inferior fronto-occipital fasciclus (bilateral), uncinate fasciclus (bilateral), superior longitudinal fasciclus (bilateral), MT+(left); | WMV: cerebellum (bilateral, crus I, crus II, lobule VI, lobule VIII, lobule IX, lobule X), premotor cortex (bilateral, corticospinal tract), corpus callosum (bilateral, genu, body), dorsolateral prefrontal cortex (bilateral), ventrolateral prefrontal cortex (bilateral), precentral gyrus (left, area 4), inferior fronto-occipital fasciclus (bilateral), uncinate fasciclus (bilateral), superior longitudinal fasciclus (bilateral), MT+(left); GMV: thalamus (left, ventral posterior lateral nucleus), rostral prefrontal cortex (bilateral, area 24, area 32), dorsolateral and ventral prefrontal cortex (bilateral, DLPFC, vPFC, area 44, area 45), premotor cortex (bilateral, area 6d, area 6mr/mc), precentral gyrus(right, area 4a/p), anterior cingulate cortex (aCG), parieto-insular vestibular cortex (bilateral, area Ig 1, area pOP, area OP2), postcentral gyrus (right, area 1, area 2 , area 3), posterior parietal cortex (bilateral, area 7a/p, area hIP1, area hIP2, area hIP3), cerebellum (bilateral, lobule X (flocculus/paraflocculus), lobule VI, lobule VIII, Crus II), area FG1, area FG2, area FG3, area FG4, entorhinal cortex, subiculum, hippocampus (DG, CA1), amygdala, occipital cortex (bilateral, area hOC1, area hOC2, area hOC3v, area hOC4v/la/lp, area hOC5 (MT+)), occipital cortex (right, area hOC3d, area hOC4d)
- `Conrad et al., 2023` | `Thalamic infarction` | `Stroke or ischemic vestibular-circuit lesions` | `ready_for_manual_review`
  Rationale: Workbook notes suggest explicit regions, quantitative imaging metrics, and a usable comparison design.
  Dedup/scope note: No duplicate or scope warning detected in the workbook triage pass.
  Region summary: thalamus (bilateral, ventral posterior lateral nucleus, ventral posterior medial nucleus, ventral lateral nucleus, medial pulvinar, ventral posterior inferior nucleus, reticular nucleus, central medial/parafascicular nucleus complex), cerebellar peduncle (bilateral, middle, superior), somatosensory cortex (bilateral, area 2v, area 3av, area S2), primary motor cortex (bilateral), insula (bilateral, retroinsular cortex, area dIg, area Ig1, area Ig2), inferior parietal lobule (bilateral, area PF, area PG), superior parietal lobule (bilateral, area 7ip, area 7r), parieto-insular vestibular cortex (bilateral, area Ri, area OP2, area OP3, area OP4), ventrolateral prefrontal cortex (bilateral), supramarginal gyrus (bilateral), inferior frontal gyrus (bilateral), cerebellum (bilateral, lobule IX, deep nuclei), corona radiata (bilateral, anterior, superior, posterior), internal capsule (bilateral, anterior limb, posterior limb, retrolenticular limb), external capsule (bilateral), sagittal stratum (bilateral), posterior thalamic radiation (bilateral), uncinate fasciculus (bilateral), superior fronto-occipital fasciculus (right), cingulum (bilateral, cingulate gyrus), tapetum (bilateral), longitudinal fasciculus (bilateral, medial, inferior), red nucleus (bilateral), brainstem (bilateral, ascending tract of Deiters, paramedian reticular formation, medial lemniscus, interstitial nucleus of Cajal)
- `Fan et al., 2022` | `Acute Vestibular Neuritis Recovery` | `Unilateral vestibular loss or deafferentation` | `ready_for_manual_review`
  Rationale: Workbook notes suggest explicit regions, quantitative imaging metrics, and a usable comparison design.
  Dedup/scope note: No duplicate or scope warning detected in the workbook triage pass.
  Region summary: Periventricular and deep subcortical white matter.
- `Gam et al., 2022` | `Cerebellar lesion` | `Stroke or ischemic vestibular-circuit lesions` | `ready_for_manual_review`
  Rationale: Workbook notes suggest explicit regions, quantitative imaging metrics, and a usable comparison design.
  Dedup/scope note: No duplicate or scope warning detected in the workbook triage pass.
  Region summary: Brainstem (vestibular nuclei, pons, medulla oblongata), cerebellum, thalamus, parieto-insular vestibular cortex, parietal cortex. through the inferior cerebellar peduncle to the cerebellar cortex, then ascending to thalamus and parietal operculum.
- `Hazzaa et al., 2022` | `White matter disease` | `White matter disease or small-vessel lesions` | `ready_for_manual_review`
  Rationale: Workbook notes suggest explicit regions, quantitative imaging metrics, and a usable comparison design.
  Dedup/scope note: No duplicate or scope warning detected in the workbook triage pass.
  Region summary: dentate nuclear region, the vestibular nuclear region (VN), the middle longitudinal fascicle (MLF), and the corticospinal tract (CST); brainstem (bilateral, III, INC, riMLF, MLF), cerebellum (bilateral, lobule X, flocculus), trigeminal toor entry zone
- `Helmchen et al., 2010` | `VN Following Recovery from Surgical Removal of Unilateral Acoustic Neuroma` | `Vestibular schwannoma resection` | `ready_for_manual_review`
  Rationale: Workbook notes suggest explicit regions, quantitative imaging metrics, and a usable comparison design.
  Dedup/scope note: No duplicate or scope warning detected in the workbook triage pass.
  Region summary: Postcentral gyrus (bilateral), MT/V5 (bilateral), cerebellum (bilateral, crus II), cerebellum (left, lobule VIIb tonsil), cerebellum (right, vermis lobule VI), superior frontal gyrus (right), middle frontal gyrus (right), orbital gyrus (left), posterior cingulate (left); Superior temporal gyrus (left, right), posterior insula, inferior parietal lobe, Heschl’s gyrus, anterolateral prefrontal cortex (left), orbitofrontal gyrus (left), fusiform gyrus (left), superior temporal gyrus (left), cerebellum (right, lobule VI), cerebellum (left, lobule VIIb), cerebellum (right, lobule IX).
- `Hong, Kim, Kim, & Lee, 2014` | `Unilateral VN Recovery` | `Unilateral vestibular loss or deafferentation` | `ready_for_manual_review`
  Rationale: Workbook notes suggest explicit regions, quantitative imaging metrics, and a usable comparison design.
  Dedup/scope note: Workbook study label normalized for year or punctuation noise.
  Region summary: Inferior frontal gyrus (right), insula (right), superior temporal sulcus (right), lingual gyrus (right), middle occipital gyrus (left), inferior occipital gyrus (left), hippocampus (bilateral), parahippocampal gyrus (bilateral), caudate nucleus (left), cerebellum (bilateral), flocculus (right); Medial superior frontal gyrus (right), middle orbital gyrus (right), cerebellar vermis, cerebellar hemisphere (right)
- `Hänggi et al., 2010` | `“Vestibular Experts” (professional ballet dancers)` | `Vestibular experts` | `ready_for_manual_review`
  Rationale: Workbook notes suggest explicit regions, quantitative imaging metrics, and a usable comparison design.
  Dedup/scope note: No duplicate or scope warning detected in the workbook triage pass.
  Region summary: Premotor cortex (left), supplementary motor area (left), putamen (left), superior frontal gyrus (left) | Corticospinal tracts (bilateral), internal capsule (bilateral), corpus callosum, anterior cingulum (left), premotor cortex (bilateral), middle frontal gyrus (left), frontal operculum (right)
- `Hüfner et al., 2011` | `“Vestibular experts” vs. non‐experts (e.g., professional dancers, slackliners)` | `Vestibular experts` | `ready_for_manual_review`
  Rationale: Workbook notes suggest explicit regions, quantitative imaging metrics, and a usable comparison design.
  Dedup/scope note: No duplicate or scope warning detected in the workbook triage pass.
  Region summary: Posterior hippocampus (bilateral), parahippocampus (bilateral); lingual gyrus (bilateral), fusiform gyrus (bilateral), thalamus (bilateral), inferior temporal gyrus (bilateral), cingulum (bilateral), cerebellum (bilateral), inferior frontal gyrus (right), gyrus rectus (right), inferior occipital gyrus (left), MT/V5 (right), temporoparietal junction (left); Hippocampus (bilateral, anterior), parieto-insular vestibular cortex (bilateral)
- `Ibitoye et al., 2022` | `Idiopathic dizziness in older adults` | `Other vestibular clinical cohorts` | `ready_for_manual_review`
  Rationale: Workbook notes suggest explicit regions, quantitative imaging metrics, and a usable comparison design.
  Dedup/scope note: No duplicate or scope warning detected in the workbook triage pass.
  Region summary: superior longitudinal fasciculus (right), inferior longitudinal fasciculus (bilateral), anterior thalamic radiation (bilateral), posterior thalamic radiation (right), corpus callosum (bilateral, genu, body, splenium central), frontal white matter (bilateral)
- `Ide et al., 2023` | `Healthy older adults` | `Healthy aging` | `ready_for_manual_review`
  Rationale: Workbook notes suggest explicit regions, quantitative imaging metrics, and a usable comparison design.
  Dedup/scope note: No duplicate or scope warning detected in the workbook triage pass.
  Region summary: Hippocampus (CA1, CA3, dentate gyrus)
- `Jacob et al., 2020` | `Age-related Saccular Loss` | `Healthy aging` | `ready_for_manual_review`
  Rationale: Workbook notes suggest explicit regions, quantitative imaging metrics, and a usable comparison design.
  Dedup/scope note: No duplicate or scope warning detected in the workbook triage pass.
  Region summary: Hippocampus (left, CA1, CA2), amygdala (left, basolateral nucleus, basomedial nucleus), entorhinal cortex (left), entorhinal-transentorhinal cortical complex (left); Thalamus (right, ventral lateral nucleus, reticular nucleus), caudate (left, ventral, ventrolateral), putamen (left, ventral, ventrolateral); Hippocampus (bilateral), entorhinal cortex (left), transentorhinal cortex (left)
- `Kirsch et al., 2016` | `Healthy adults` | `Healthy non-clinical cohorts` | `ready_for_manual_review`
  Rationale: Workbook notes suggest explicit regions, quantitative imaging metrics, and a usable comparison design.
  Dedup/scope note: No duplicate or scope warning detected in the workbook triage pass.
  Region summary: Pons (bilateral, medial vestibular nucleus, lateral vestibular nucleus, vestibular nerve, medial lemniscus, medial longitudinal fascicle [mesencephalic crossing tract]; ipsilateral, medial vestibular nucleus, parvocellular reticular nucleus, medial lemniscus, subependymal layer [ipsilateral direct and indirect tracts], pontine nuclei [pontine crossing tract], dorsal paragigantocellular nucleus [mesencephalic crossing tract]; contralateral, vestibular nerve, lateral vestibular nucleus, medial lemniscus, gigantocellular nucleus, medial superior olivary nucleus, lateral superior olivary nucleus, periolivary complex [pontine crossing tract]), Midbrain (bilateral, medial longitudinal fascicle, oculomotor nucleus [mesencephalic crossing tract], mesencephalic longitudinal formation, medial lemniscus [pontine crossing tract]; ipsilateral: substantia nigra pars compacta [ipsilateral direct tract], mesencephalic longitudinal formation, periaqueductal gray lateral part, pedunculopontine nucleus pars dissipata, superior colliculus [ipsilateral indirect tract]; contralateral: superior cerebellar peduncle, brachium of inferior colliculus [pontine crossing tract], caudal linear nucleus [mesencephalic crossing tract]), Thalamus, posterolateral (bilateral: lateral posterior nucleus, ventral posterior lateral nucleus, pulvinar nucleus [anterior, lateral, medial subdivisions] [ipsilateral indirect and pontine crossing tracts]; contralateral: ventral posterior medial nucleus, ventral posterior lateral nucleus [posterior and anterior subdivisions], pulvinar nucleus [anterior, medial subdivisions], lateral posterior nucleus, reticular thalamic nucleus, zona incerta [mesencephalic crossing tract]), Thalamus, paramedian (ipsilateral: central lateral nucleus posterior part, centromedian nucleus [ipsilateral indirect tract]), Cerebral white matter (bilateral: internal capsule [all tracts], corpus callosum splenium [interhemispheric])
- `Kwon & Byun, 2023` | `Healthy adults` | `Healthy non-clinical cohorts` | `ready_for_manual_review`
  Rationale: Workbook notes suggest explicit regions, quantitative imaging metrics, and a usable comparison design.
  Dedup/scope note: No duplicate or scope warning detected in the workbook triage pass.
  Region summary: Parieto‐insular cortex (bilateral, OP2), caudate nucleus (bilateral), thalamus (bilateral), insula (bilateral), precuneus (bilateral), Rolandic operculum (bilateral)
- `Nigmatullina et al., 2015` | `“Vestibular Experts” (professional dancers)` | `Vestibular experts` | `ready_for_manual_review`
  Rationale: Workbook notes suggest explicit regions, quantitative imaging metrics, and a usable comparison design.
  Dedup/scope note: No duplicate or scope warning detected in the workbook triage pass.
  Region summary: Cerebellum (bilateral, lobule VIII, lobule IX). | Superior longitudinal fasciculus (bilateral, temporoparietal junction), infeirior fronto-occipital fasciculus (bilateral), anterior thalamic radiation (bilateral) .
- `Park et al., 2021` | `Stroke/lesion in PIVC region` | `Stroke or ischemic vestibular-circuit lesions` | `ready_for_manual_review`
  Rationale: Workbook notes suggest explicit regions, quantitative imaging metrics, and a usable comparison design.
  Dedup/scope note: Workbook study label normalized for year or punctuation noise.
  Region summary: parieto‐insular vestibular cortex tract (bilateral), parieto‐insular vestibular cortex (bilateral), brainstem (bilateral, vestibular nuclei), thalamus (bilateral)
- `Popp et al., 2018` | `Phobic postural vertigo` | `Other vestibular clinical cohorts` | `ready_for_manual_review`
  Rationale: Workbook notes suggest explicit regions, quantitative imaging metrics, and a usable comparison design.
  Dedup/scope note: No duplicate or scope warning detected in the workbook triage pass.
  Region summary: Thalamus (bilateral, mediodorsal nucleus), precentral gyrus; Cerebellum (bilateral), supramarginal gyrus (left), posterior middle frontal gyrus (right); Ventromedial prefrontal cortex, insular sulcus (left), lingual gyrus (left), anterior cingulate gyrus (right), cuneus (right).
- `Rogge et al., 2018` | `Healthy adults (balance training)` | `Healthy non-clinical cohorts` | `ready_for_manual_review`
  Rationale: Workbook notes suggest explicit regions, quantitative imaging metrics, and a usable comparison design.
  Dedup/scope note: No duplicate or scope warning detected in the workbook triage pass.
  Region summary: Superior temporal gyrus (left), circular insular sulcus (left), superior transverse occipital sulcus (left), superior frontal sulcus (left), posterior cingulate gyrus (right), precentral gyrus (bilateral), pericalcarine gyrus (right), putamen (bilateral).
- `Trakolis et al., 2021` | `Chronic tinnitus after vestibular schwannoma resection` | `Vestibular schwannoma resection` | `ready_for_manual_review`
  Rationale: Workbook notes suggest explicit regions, quantitative imaging metrics, and a usable comparison design.
  Dedup/scope note: No duplicate or scope warning detected in the workbook triage pass.
  Region summary: Fusiform gyrus (left), medial temporal gyrus (left), superior colliculus (right), inferior frontal gyrus (left, pars orbitalis), medial superior frontal gyrus (left) paracentral lobule (left), caudate nucleus (bilateral).
- `Van Impe et al., 2012` | `Healthy young vs healthy older adults` | `Healthy aging` | `ready_for_manual_review`
  Rationale: Workbook notes suggest explicit regions, quantitative imaging metrics, and a usable comparison design.
  Dedup/scope note: No duplicate or scope warning detected in the workbook triage pass.
  Region summary: frontal forceps (bilateral), genu of the corpus callosum, occipital forceps (bilateral)
- `Wang et al., 2019` | `Vestibular migraine (VM), migraine without aura (MWoA)` | `Vestibular migraine` | `ready_for_manual_review`
  Rationale: Workbook notes suggest explicit regions, quantitative imaging metrics, and a usable comparison design.
  Dedup/scope note: No duplicate or scope warning detected in the workbook triage pass.
  Region summary: medial superior frontal gyrus (right), angular gyrus (right), middle frontal gyrus (left), supplementary motor area (right)
- `Yeo et al., 2017` | `Stroke (MCA territory infarction confined to parieto‐insular vestibular cortex)` | `Stroke or ischemic vestibular-circuit lesions` | `ready_for_manual_review`
  Rationale: Workbook notes suggest explicit regions, quantitative imaging metrics, and a usable comparison design.
  Dedup/scope note: No duplicate or scope warning detected in the workbook triage pass.
  Region summary: parietal-insular vestibular cortex (bilateral), thalamus (bilateral), brainstem (bilateral, vestibular nulcei), corticospinal tract (bilateral)
- `Yeo et al., 2018` | `Lateral medullary (Wallenberg) syndrome` | `Stroke or ischemic vestibular-circuit lesions` | `ready_for_manual_review`
  Rationale: Workbook notes suggest explicit regions, quantitative imaging metrics, and a usable comparison design.
  Dedup/scope note: No duplicate or scope warning detected in the workbook triage pass.
  Region summary: Parietal-insular vestibular cortex (bilateral), brainstem (bilateral, vestibular nulcei)
- `Yeo et al., 2020` | `Healthy younger vs. older` | `Healthy aging` | `ready_for_manual_review`
  Rationale: Workbook notes suggest explicit regions, quantitative imaging metrics, and a usable comparison design.
  Dedup/scope note: No duplicate or scope warning detected in the workbook triage pass.
  Region summary: brainstem (bilateral, medial vestibular nucleus, lateral vestibular nucleus, reticular nucleus, vestibulo spinal tract), thalamus (bilateral, ventral posterior lateral nucleus), parieto‐insular vestibular cortex (bilateral)
- `Conrad et al., 2022` | `Infarcts of the subcortical vestibular circuitry` | `Stroke or ischemic vestibular-circuit lesions` | `hold_author_year_collision`
  Rationale: Workbook notes suggest explicit regions, quantitative imaging metrics, and a usable comparison design.
  Dedup/scope note: Workbook study label normalized for year or punctuation noise. Another missing-study row shares this author-year signature; resolve same-year paper versus duplicate before extraction.
  Region summary: Cerebellum (bilateral, dentate nucleus, crus I, crus II, lobule VI, lobule VIIB, lobule VIIIa, lobule IX, lobule X), cerebellum (ocular motor vermis, lobules V–VII, VI, VII, VIIIab), cerebellum (motor, lobules V, VII), cerebellum (fastigial nucleus), visual cortex (bilateral, area MT+, dorsal visual stream, ventral visual stream, primary, higher order), parietal cortex (bilateral, inferior parietal lobule, lateral intraparietal area, ventral intraparietal area, areas 7AL, 7PC), thalamus (medial nucleus, mediodorsal nucleus, pulvinar nucleus), frontal eye fields, area 6d, postcentral gyrus (right, areas 1, 2, 3b), precentral gyrus (right, areas 1, 3b), putamen, parieto-insular vestibular cortex (parieto-opercular, retro-insular vestibular cortex), splenium of the corpus callosum
- `Fettrow et al., 2023` | `Healthy younger & older adults; Healthy younger vs. older adults` | `Healthy aging` | `hold_scope_split`
  Rationale: Workbook notes suggest explicit regions, quantitative imaging metrics, and a usable comparison design.
  Dedup/scope note: Workbook entry mixes multiple conditions, frames, or cohort types and should be split or scoped before review.
  Region summary: Superior frontal gyrus (left, pars opercularis), cerebellum (left, lobule V), cerebellum (right, lobule VIIB, lobule VIII), precentral gyrus (right), postcentral gyrus (bilateral), insula (left), superior temporal gyrus (left), transverse temporal gyrus (left), supramarginal gyrus (right) | Corticospinal tract (right), inferior longitudinal fasciculus (right)
- `Hummel et al., 2014` | `Bilateral vestibulopathy (BVP), "Vestibular Experts"` | `Needs manual scope decision` | `hold_scope_split`
  Rationale: Workbook notes suggest explicit regions, quantitative imaging metrics, and a usable comparison design.
  Dedup/scope note: Workbook entry mixes multiple conditions, frames, or cohort types and should be split or scoped before review.
  Region summary: Corpus callosum (bilateral, body, splenium), cingulum, anterior thalamic radiation (right), external capsule (left), internal capsule, forceps minor (bilateral), forceps major (bilateral), fornix (bilateral), inferior fronto-ocipital fasciculus (bilateral), uncinate fasciculus (left), superior longitudinal fascisulus (left), corticospinal tract (left)
- `Hupfeld et al., 2022` | `Healthy younger & older adults; Healthy younger vs. older adults; Long‐duration spaceflight (astronauts)` | `Healthy aging` | `hold_scope_split`
  Rationale: Workbook notes suggest explicit regions, quantitative imaging metrics, and a usable comparison design.
  Dedup/scope note: Workbook entry mixes multiple conditions, frames, or cohort types and should be split or scoped before review.
  Region summary: Supramarginal gyrus (left), postcentral gyrus (left), superior temporal sulcus bank (left), superior frontal gyrus (left), lingual gyrus (left), lateral orbitofrontal cortex (right) | Precentral gyrus (left), superior parietal lobule (left), superior temporal gyrus (right) | Corpus callosum (bilateral, genu, body, splenium), forceps minor (left), cingulum (left), superior longitudinal fasciculus (right), superior corona radiata (right), corticospinal tract (right), posterior corona radiata (right), anterior thalamic radiation (right), inferior fronto-occipital fasciculus (right)
- `McGregor et al., 2023` | `Long‐duration spaceflight (astronauts); Varied duration spaceflight (astronauts)` | `Spaceflight-related vestibular adaptation` | `hold_scope_split`
  Rationale: Workbook notes suggest explicit regions, quantitative imaging metrics, and a usable comparison design.
  Dedup/scope note: Workbook entry mixes multiple conditions, frames, or cohort types and should be split or scoped before review.
  Region summary: Third ventricle (bilateral), lateral ventricle (right) | interhemispheric fissure, lateral fissure, lateral ventricle (right)
- `Conrad et al., 2022` | `Unilateral subcortical or infratentorial ischemic stroke; Unilateral thalamic or brainstem infarction` | `Stroke or ischemic vestibular-circuit lesions` | `hold_author_year_collision_and_scope_split`
  Rationale: Workbook notes suggest explicit regions, quantitative imaging metrics, and a usable comparison design.
  Dedup/scope note: Another missing-study row shares this author-year signature; resolve same-year paper versus duplicate before extraction. Workbook entry mixes multiple conditions, frames, or cohort types and should be split or scoped before review.
  Region summary: dentate nuclear region, the vestibular nuclear region (VN), the middle longitudinal fascicle (MLF), and the corticospinal tract (CST); brainstem (bilateral, III, INC, riMLF, MLF), cerebellum (bilateral, lobule X, flocculus), trigeminal toor entry zone (bilateral, V root entry zone), medial lemniscus (bilateral) (ML), superior colliculus (bilateral), parieto-opercular / (retro-) insular cortex (PIVC), premotor cortex, somatosensory cortex (bilateral), cingulate cortex (bilateral), corpus callosum (splenium, CC5, CC6, CC7) | primary somatosensory cortex (right, area 1, area 2), parieto-opercular (retro-) insular vestibular cortex (right), cerebellum (bilateral, lobule X), MT+ (bilateral)

## Medium Priority

- `Choi et al., 2015` | `Unilateral inferior cerebellar peduncle (ICP) lesion` | `Stroke or ischemic vestibular-circuit lesions` | `ready_for_manual_review`
  Rationale: Workbook notes suggest potential ROI-level findings, but the paper must be checked for convertible statistics.
  Dedup/scope note: No duplicate or scope warning detected in the workbook triage pass.
- `Dordevic et al., 2021` | `Chronic, mild vestibulopathy` | `Chronic or mild vestibulopathy` | `ready_for_manual_review`
  Rationale: Workbook notes suggest potential ROI-level findings, but the paper must be checked for convertible statistics.
  Dedup/scope note: No duplicate or scope warning detected in the workbook triage pass.
- `Gamba & Pavia, 2016` | `Vascular vertigo` | `Stroke or ischemic vestibular-circuit lesions` | `ready_for_manual_review`
  Rationale: Workbook notes suggest potential ROI-level findings, but the paper must be checked for convertible statistics.
  Dedup/scope note: No duplicate or scope warning detected in the workbook triage pass.
- `Indovina et al., 2020` | `Healthy young adults` | `Healthy non-clinical cohorts` | `ready_for_manual_review`
  Rationale: Workbook notes suggest potential ROI-level findings, but the paper must be checked for convertible statistics.
  Dedup/scope note: No duplicate or scope warning detected in the workbook triage pass.
- `Jian et al., 2024` | `Late‐stage MD` | `Meniere's disease` | `ready_for_manual_review`
  Rationale: Workbook notes suggest potential ROI-level findings, but the paper must be checked for convertible statistics.
  Dedup/scope note: No duplicate or scope warning detected in the workbook triage pass.
- `Kamil, Jacob, Ratnanather, Resnick, & Agrawal, 2018` | `Age-related Saccular, Utricular, and Horizontal Semicircular Canal Loss` | `Healthy aging` | `ready_for_manual_review`
  Rationale: Workbook notes suggest potential ROI-level findings, but the paper must be checked for convertible statistics.
  Dedup/scope note: No duplicate or scope warning detected in the workbook triage pass.
- `Kim et al., 2017` | `Brainstem / cerebellar stroke` | `Stroke or ischemic vestibular-circuit lesions` | `ready_for_manual_review`
  Rationale: Workbook notes suggest potential ROI-level findings, but the paper must be checked for convertible statistics.
  Dedup/scope note: No duplicate or scope warning detected in the workbook triage pass.
- `Kirsch et al., 2018` | `Healthy adults` | `Healthy non-clinical cohorts` | `ready_for_manual_review`
  Rationale: Workbook notes suggest potential ROI-level findings, but the paper must be checked for convertible statistics.
  Dedup/scope note: No duplicate or scope warning detected in the workbook triage pass.
- `Noohi et al., 2020` | `Healthy younger vs. older adults` | `Healthy aging` | `ready_for_manual_review`
  Rationale: Workbook notes suggest potential ROI-level findings, but the paper must be checked for convertible statistics.
  Dedup/scope note: No duplicate or scope warning detected in the workbook triage pass.
- `Padova et al., 2021` | `Age-related Saccular, Utricular, and Horizontal Semicircular Canal Loss` | `Healthy aging` | `ready_for_manual_review`
  Rationale: Workbook notes suggest potential ROI-level findings, but the paper must be checked for convertible statistics.
  Dedup/scope note: Workbook study label normalized for year or punctuation noise.
- `Raiser et al., 2020` | `Healthy young adults` | `Healthy non-clinical cohorts` | `ready_for_manual_review`
  Rationale: Workbook notes suggest potential ROI-level findings, but the paper must be checked for convertible statistics.
  Dedup/scope note: No duplicate or scope warning detected in the workbook triage pass.
- `Shen et al., 2023` | `Vestibular migraine (VM)` | `Vestibular migraine` | `ready_for_manual_review`
  Rationale: Workbook notes suggest potential ROI-level findings, but the paper must be checked for convertible statistics.
  Dedup/scope note: No duplicate or scope warning detected in the workbook triage pass.
- `Smith et al., 2021` | `Post‐concussive vestibular dysfunction` | `Post-traumatic or concussive vestibulopathy` | `ready_for_manual_review`
  Rationale: Workbook notes suggest potential ROI-level findings, but the paper must be checked for convertible statistics.
  Dedup/scope note: No duplicate or scope warning detected in the workbook triage pass.
- `Wirth et al., 2018` | `Healthy adults` | `Healthy non-clinical cohorts` | `ready_for_manual_review`
  Rationale: Workbook notes suggest potential ROI-level findings, but the paper must be checked for convertible statistics.
  Dedup/scope note: No duplicate or scope warning detected in the workbook triage pass.
- `Yeo et al., 2024` | `Healthy young vs. healthy older adults` | `Healthy aging` | `ready_for_manual_review`
  Rationale: Workbook notes suggest potential ROI-level findings, but the paper must be checked for convertible statistics.
  Dedup/scope note: No duplicate or scope warning detected in the workbook triage pass.

## Low Priority

- `Ruehl et al., 2022` | `Healthy young adults` | `Healthy non-clinical cohorts` | `ready_for_manual_review`
  Rationale: Workbook notes do not yet suggest a reliable ROI-wise effect-size extraction path.
  Dedup/scope note: No duplicate or scope warning detected in the workbook triage pass.
- `Hadi et al., 2022` | `Healthy + lesion or normal variants` | `Needs manual scope decision` | `hold_scope_split`
  Rationale: Condition label mixes scientific axes and should be resolved before extraction.
  Dedup/scope note: Workbook study label normalized for year or punctuation noise. Workbook entry mixes multiple conditions, frames, or cohort types and should be split or scoped before review.
- `Ibitoye et al., 2023` | `Review or combined study on “OP2” region` | `Needs manual scope decision` | `hold_scope_split`
  Rationale: Review or composite framing rather than a single extractable empirical cohort.
  Dedup/scope note: Workbook entry mixes multiple conditions, frames, or cohort types and should be split or scoped before review.
- `Oussoren et al., 2022` | `Vestibular neuritis + cerebral small vessel disease` | `Needs split across vestibular and vascular axes` | `hold_scope_split`
  Rationale: Condition label mixes scientific axes and should be resolved before extraction.
  Dedup/scope note: Workbook entry mixes multiple conditions, frames, or cohort types and should be split or scoped before review.

## Machine-Readable Output

- See `missing_study_triage.csv` for the full triage table.
