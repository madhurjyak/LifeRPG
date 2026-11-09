// The Seven-Phase Ascension Life RPG Engine & Reactive Alpine Controller
// Calm Wuxia Aesthetic Edition — Daoist Cultivation & Qi Harmony

// ====================================================================
// PROCEDURAL SOUND SYNTHESIZER (CALM EASTERN ACOUSTICS)
// ====================================================================
class SoundSynthesizer {
    constructor() {
        this.ctx = null;
        this.muted = localStorage.getItem('life_rpg_muted') === 'true';
    }

    init() {
        if (!this.ctx) {
            const AudioCtx = window.AudioContext || window.webkitAudioContext;
            if (AudioCtx) {
                this.ctx = new AudioCtx();
            }
        }
        if (this.ctx && this.ctx.state === 'suspended') {
            this.ctx.resume();
        }
    }

    toggleMute() {
        this.muted = !this.muted;
        localStorage.setItem('life_rpg_muted', this.muted);
        return this.muted;
    }

    // Peaceful Singing Bowl / Jade Chime (528 Hz Harmonic Fundamental)
    playQuestComplete() {
        if (this.muted) return;
        this.init();
        if (!this.ctx) return;

        const now = this.ctx.currentTime;
        // 528 Hz (fundamental) + 792 Hz + 1056 Hz (pure harmonic partials)
        const partials = [
            { f: 528, gain: 0.22, decay: 1.4 },
            { f: 792, gain: 0.12, decay: 1.0 },
            { f: 1056, gain: 0.06, decay: 0.7 }
        ];

        partials.forEach(p => {
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();
            osc.type = 'sine';
            osc.frequency.setValueAtTime(p.f, now);

            gain.gain.setValueAtTime(0, now);
            gain.gain.linearRampToValueAtTime(p.gain, now + 0.02);
            gain.gain.exponentialRampToValueAtTime(0.0001, now + p.decay);

            osc.connect(gain);
            gain.connect(this.ctx.destination);

            osc.start(now);
            osc.stop(now + p.decay + 0.05);
        });
    }

    // Temple Wooden Fish (Muyu) / Bamboo Strike
    playBossHit() {
        if (this.muted) return;
        this.init();
        if (!this.ctx) return;

        const now = this.ctx.currentTime;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        const filter = this.ctx.createBiquadFilter();

        osc.type = 'triangle';
        osc.frequency.setValueAtTime(420, now);
        osc.frequency.exponentialRampToValueAtTime(160, now + 0.12);

        filter.type = 'bandpass';
        filter.frequency.setValueAtTime(650, now);
        filter.Q.setValueAtTime(3.0, now);

        gain.gain.setValueAtTime(0.35, now);
        gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.14);

        osc.connect(filter);
        filter.connect(gain);
        gain.connect(this.ctx.destination);

        osc.start(now);
        osc.stop(now + 0.16);
    }

    // Pure Jade Pendant Clink
    playGoldClink() {
        if (this.muted) return;
        this.init();
        if (!this.ctx) return;

        const now = this.ctx.currentTime;
        [1760, 2640].forEach((freq, i) => {
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();
            osc.type = 'sine';
            osc.frequency.setValueAtTime(freq, now + i * 0.07);

            gain.gain.setValueAtTime(0, now + i * 0.07);
            gain.gain.linearRampToValueAtTime(0.12, now + i * 0.07 + 0.01);
            gain.gain.exponentialRampToValueAtTime(0.0001, now + i * 0.07 + 0.35);

            osc.connect(gain);
            gain.connect(this.ctx.destination);

            osc.start(now + i * 0.07);
            osc.stop(now + i * 0.07 + 0.4);
        });
    }

    // Daoist Temple Bronze Gong / Realm Breakthrough
    playLevelUp() {
        if (this.muted) return;
        this.init();
        if (!this.ctx) return;

        const now = this.ctx.currentTime;
        // Deep warm bronze bell overtones
        const gongHarmonics = [
            { f: 196.00, gain: 0.30, decay: 2.2 }, // G3
            { f: 293.66, gain: 0.18, decay: 1.8 }, // D4
            { f: 392.00, gain: 0.15, decay: 1.5 }, // G4
            { f: 587.33, gain: 0.09, decay: 1.2 }, // D5
            { f: 783.99, gain: 0.05, decay: 0.9 }  // G5
        ];

        gongHarmonics.forEach(h => {
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();
            osc.type = 'sine';
            osc.frequency.setValueAtTime(h.f, now);

            gain.gain.setValueAtTime(0, now);
            gain.gain.linearRampToValueAtTime(h.gain, now + 0.03);
            gain.gain.exponentialRampToValueAtTime(0.0001, now + h.decay);

            osc.connect(gain);
            gain.connect(this.ctx.destination);

            osc.start(now);
            osc.stop(now + h.decay + 0.05);
        });
    }

    // Celestial Bell & Inner Demon Quelled
    playBossDefeat() {
        if (this.muted) return;
        this.init();
        if (!this.ctx) return;

        const now = this.ctx.currentTime;
        // Sustained meditative bell resonance
        const chord = [220.00, 330.00, 440.00, 550.00, 660.00];
        chord.forEach((f, idx) => {
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();
            osc.type = 'sine';
            osc.frequency.setValueAtTime(f, now + idx * 0.06);

            gain.gain.setValueAtTime(0, now + idx * 0.06);
            gain.gain.linearRampToValueAtTime(0.15, now + idx * 0.06 + 0.05);
            gain.gain.exponentialRampToValueAtTime(0.0001, now + idx * 0.06 + 2.5);

            osc.connect(gain);
            gain.connect(this.ctx.destination);

            osc.start(now + idx * 0.06);
            osc.stop(now + idx * 0.06 + 2.6);
        });
    }
}

const soundSynth = new SoundSynthesizer();

// ====================================================================
// ALPINE.JS STATE STORE & UI CONTROLLER
// ====================================================================
function lifeRpgApp() {
    return {
        activeTab: 'command', // 'command', 'crucible', 'reliquary', 'oracle'
        loading: true,
        soundMuted: soundSynth.muted,
        bossHurt: false,
        toasts: [],

        // Core HUD State
        user: {},
        levelInfo: {},
        pillarInfo: { MIND: {}, HEALTH: {}, CAREER: {}, WEALTH: {} },
        streakMultiplier: 1.0,
        campaigns: [],
        quests: [],
        questFilterAttr: 'ALL',
        questFilterStatus: 'ALL',

        get filteredQuests() {
            return this.quests.filter(q => {
                const matchAttr = this.questFilterAttr === 'ALL' || q.attribute_type === this.questFilterAttr;
                const matchStatus = this.questFilterStatus === 'ALL' ||
                    (this.questFilterStatus === 'ACTIVE' && !q.is_completed) ||
                    (this.questFilterStatus === 'COMPLETED' && q.is_completed);
                return matchAttr && matchStatus;
            });
        },

        recentLogs: [],
        reliquaryItems: [],
        oracleData: {},

        // Modals
        showNewCampaignModal: false,
        newCampaign: { goal_title: '', description: '', difficulty_focus: 'BALANCED', target_date: '' },
        creatingCampaign: false,

        showNewQuestModal: false,
        newQuest: { task_name: '', attribute_type: 'MIND', difficulty_rank: 'C', campaign_id: null },
        creatingQuest: false,

        showNewRewardModal: false,
        newReward: { item_name: '', item_description: '', gold_cost: 50, icon_name: 'sparkles', item_type: 'IRL_REWARD' },
        creatingReward: false,

        // Crucible Meditation Chamber
        crucible: {
            durationMinutes: 25,
            timeLeft: 25 * 60,
            isRunning: false,
            interval: null,
            attributeType: 'MIND',
            campaignId: null
        },

        // Grimoire Log Form
        journalInput: '',
        submittingJournal: false,
        latestLogAnalysis: null,

        // Oracle Prophecy State
        prophecyLoading: false,
        currentProphecy: null,

        // Charts references
        radarChart: null,
        velocityChart: null,

        init() {
            this.fetchHud().then(() => {
                this.$nextTick(() => {
                    this.initIcons();
                    this.initCharts();
                });
            });
        },

        initIcons() {
            if (window.lucide) {
                window.lucide.createIcons();
            }
        },

        toggleAudio() {
            this.soundMuted = soundSynth.toggleMute();
            this.showToast("Meditation Chimes", this.soundMuted ? "Temple Bell Silenced" : "Temple Bell Harmonized", "info");
        },

        async seedSampleData() {
            if (!confirm("Populate Sanctuary with rich sample cultivation data (4 Pillar Campaigns, Deeds, Grimoire logs, and Relics)?")) {
                return;
            }
            this.loading = true;
            try {
                const res = await fetch('/api/demo/seed', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ force: true })
                });
                const data = await res.json();
                if (data.success) {
                    soundSynth.playGong();
                    this.triggerConfetti(true);
                    await this.fetchHud();
                    this.showToast("Sanctuary Replenished", "Rich cultivation data loaded across all 4 pillars!", "success");
                } else {
                    this.showToast("Seed Failed", data.error || "Could not populate data", "warning");
                }
            } catch (err) {
                console.error("Seed error:", err);
                this.showToast("Connection Error", "Failed to contact sanctuary server", "error");
            } finally {
                this.loading = false;
            }
        },

        showToast(title, message, type = 'success') {
            const id = Date.now() + Math.random();
            this.toasts.push({ id, title, message, type });
            setTimeout(() => {
                this.toasts = this.toasts.filter(t => t.id !== id);
            }, 4500);
        },

        triggerConfetti(epic = false) {
            if (typeof confetti === 'function') {
                if (epic) {
                    confetti({
                        particleCount: 80,
                        spread: 80,
                        origin: { y: 0.6 },
                        colors: ['#0d9488', '#b45309', '#b91c1c', '#d97706', '#f5f2eb']
                    });
                } else {
                    confetti({
                        particleCount: 40,
                        spread: 50,
                        origin: { y: 0.7 },
                        colors: ['#0d9488', '#b45309', '#d97706']
                    });
                }
            }
        },

        async fetchHud() {
            try {
                const res = await fetch('/api/hud');
                if (!res.ok) throw new Error("Sanctuary sync failure");
                const data = await res.json();

                this.user = data.user;
                this.levelInfo = data.level_info;
                this.pillarInfo = data.pillar_info;
                this.streakMultiplier = data.streak_multiplier;
                this.campaigns = data.campaigns;
                this.quests = data.quests;
                this.recentLogs = data.recent_logs;
                this.reliquaryItems = data.reliquary_items;
                this.oracleData = data.oracle;

                if (this.campaigns.length > 0 && !this.crucible.campaignId) {
                    this.crucible.campaignId = this.campaigns[0].id;
                }

                this.loading = false;
                this.updateCharts();
                this.$nextTick(() => this.initIcons());
            } catch (err) {
                console.error("Fetch HUD error:", err);
                this.loading = false;
            }
        },

        // ----------------------------------------------------
        // PHASE II: QUESTS / DAILY CULTIVATION DEEDS
        // ----------------------------------------------------
        async completeQuest(questId) {
            try {
                soundSynth.playQuestComplete();
                const res = await fetch(`/api/complete_quest/${questId}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                const data = await res.json();
                if (!res.ok) throw new Error(data.error || "Deed record failed");

                if (data.already_completed) {
                    this.showToast("Notice", "Deed already fulfilled and consecrated.", "info");
                    return;
                }

                soundSynth.playBossHit();
                soundSynth.playGoldClink();

                this.bossHurt = true;
                setTimeout(() => { this.bossHurt = false; }, 600);

                if (data.boss_defeated) {
                    soundSynth.playBossDefeat();
                    this.triggerConfetti(true);
                    this.showToast("TRIBULATION QUELLED!", `Inner Demon '${data.defeated_boss_name || 'Tribulation'}' dispelled! +500 Qi & +200 Spirit Stones harvested.`, "success");
                } else if (data.phase_advanced) {
                    soundSynth.playLevelUp();
                    this.triggerConfetti(true);
                    this.showToast("REALM BREAKTHROUGH!", `Ascended to Realm Phase ${data.new_phase}!`, "success");
                } else if (data.leveled_up) {
                    soundSynth.playLevelUp();
                    this.triggerConfetti(false);
                    this.showToast("CULTIVATION ELEVATION!", `Attained Level ${data.new_level}!`, "success");
                } else {
                    this.showToast("Deed Consecrated", `+${data.xp_gained} Qi • +${data.gold_gained} Spirit Stones channeled`, "success");
                }

                if (data.shield_used) {
                    this.showToast("Chronos Talisman", data.streak_message, "info");
                }

                await this.fetchHud();
            } catch (err) {
                this.showToast("Deed Error", err.message, "error");
            }
        },

        async submitCustomQuest() {
            if (!this.newQuest.task_name.trim()) return;
            this.creatingQuest = true;
            try {
                const res = await fetch('/api/quests', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(this.newQuest)
                });
                const data = await res.json();
                if (!res.ok) throw new Error(data.error || "Failed to inscribe deed");

                soundSynth.playQuestComplete();
                this.showToast("Deed Inscribed", `New ${this.newQuest.attribute_type} cultivation practice recorded.`, "success");
                this.showNewQuestModal = false;
                this.newQuest.task_name = '';
                await this.fetchHud();
            } catch (err) {
                this.showToast("Error", err.message, "error");
            } finally {
                this.creatingQuest = false;
            }
        },

        // ----------------------------------------------------
        // PHASE I: THE VOW (CAMPAIGN CREATION)
        // ----------------------------------------------------
        async submitCampaign() {
            if (!this.newCampaign.goal_title.trim()) return;
            this.creatingCampaign = true;
            try {
                const res = await fetch('/api/campaign', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(this.newCampaign)
                });
                const data = await res.json();
                if (!res.ok) throw new Error(data.error || "Failed to establish vow");

                soundSynth.playLevelUp();
                this.triggerConfetti(true);
                this.showToast("Vow Sealed", `Tribulation '${data.campaign.boss_name}' manifested with ${data.quests.length} cultivation deeds.`, "success");

                this.showNewCampaignModal = false;
                this.newCampaign = { goal_title: '', description: '', difficulty_focus: 'BALANCED', target_date: '' };
                await this.fetchHud();
            } catch (err) {
                this.showToast("Vow Error", err.message, "error");
            } finally {
                this.creatingCampaign = false;
            }
        },

        // ----------------------------------------------------
        // PHASE III: THE CRUCIBLE (MEDITATION PAVILION)
        // ----------------------------------------------------
        setCrucibleDuration(mins) {
            if (this.crucible.isRunning) return;
            this.crucible.durationMinutes = mins;
            this.crucible.timeLeft = mins * 60;
        },

        startCrucible() {
            if (this.crucible.isRunning) return;
            soundSynth.init();
            this.crucible.isRunning = true;
            this.crucible.interval = setInterval(() => {
                if (this.crucible.timeLeft > 0) {
                    this.crucible.timeLeft--;
                } else {
                    this.finishCrucible();
                }
            }, 1000);
        },

        pauseCrucible() {
            this.crucible.isRunning = false;
            if (this.crucible.interval) {
                clearInterval(this.crucible.interval);
                this.crucible.interval = null;
            }
        },

        resetCrucible() {
            this.pauseCrucible();
            this.crucible.timeLeft = this.crucible.durationMinutes * 60;
        },

        formatCrucibleTime() {
            const mins = Math.floor(this.crucible.timeLeft / 60);
            const secs = this.crucible.timeLeft % 60;
            return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
        },

        getCrucibleProgress() {
            const total = this.crucible.durationMinutes * 60;
            const elapsed = total - this.crucible.timeLeft;
            return Math.min(100, Math.max(0, (elapsed / total) * 100));
        },

        async finishCrucible() {
            this.pauseCrucible();
            soundSynth.playLevelUp();
            this.triggerConfetti(false);

            try {
                const res = await fetch('/api/crucible/complete', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        duration_minutes: this.crucible.durationMinutes,
                        attribute_type: this.crucible.attributeType,
                        campaign_id: this.crucible.campaignId
                    })
                });
                const data = await res.json();
                if (!res.ok) throw new Error(data.error || "Meditation record error");

                soundSynth.playBossHit();
                this.bossHurt = true;
                setTimeout(() => { this.bossHurt = false; }, 600);

                if (data.boss_defeated) {
                    soundSynth.playBossDefeat();
                    this.triggerConfetti(true);
                    this.showToast("TRIBULATION CLEARED IN MEDITATION!", `'${data.defeated_boss_name}' overcome through tranquil focus! +500 Qi bonus!`, "success");
                } else {
                    this.showToast("Meditation Complete", `+${data.xp_gained} Qi • +${data.gold_gained} Spirit Stones • ${data.boss_damage_dealt} Tribulation Purged`, "success");
                }

                this.resetCrucible();
                await this.fetchHud();
            } catch (err) {
                this.showToast("Meditation Error", err.message, "error");
            }
        },

        // ----------------------------------------------------
        // PHASE IV: THE GRIMOIRE (DAOIST CHRONICLE & REFLECTION)
        // ----------------------------------------------------
        async submitJournal() {
            if (!this.journalInput.trim()) return;
            this.submittingJournal = true;
            try {
                soundSynth.playQuestComplete();
                const res = await fetch('/api/journal', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ journal_content: this.journalInput })
                });
                const data = await res.json();
                if (!res.ok) throw new Error(data.error || "Failed to inscribe chronicle");

                soundSynth.playGoldClink();
                this.latestLogAnalysis = data.log;
                this.journalInput = '';
                this.showToast("Chronicle Sealed", `+${data.xp_awarded} Contemplation Qi awarded. Mentor wisdom received.`, "success");
                await this.fetchHud();
            } catch (err) {
                this.showToast("Chronicle Error", err.message, "error");
            } finally {
                this.submittingJournal = false;
            }
        },

        // ----------------------------------------------------
        // PHASE VI: THE RELIQUARY (PAVILION OF TREASURES)
        // ----------------------------------------------------
        async buyItem(item) {
            try {
                const res = await fetch(`/api/reliquary/buy/${item.id}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                const data = await res.json();
                if (!res.ok) throw new Error(data.error || "Exchange denied");

                soundSynth.playGoldClink();
                this.triggerConfetti(false);
                this.showToast("Relic Exchanged", data.message, "success");
                await this.fetchHud();
            } catch (err) {
                this.showToast("Pavilion Notice", err.message, "error");
            }
        },

        async submitCustomReward() {
            if (!this.newReward.item_name.trim() || !this.newReward.gold_cost) return;
            this.creatingReward = true;
            try {
                const res = await fetch('/api/reliquary/create', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(this.newReward)
                });
                const data = await res.json();
                if (!res.ok) throw new Error(data.error || "Failed to forge relic");

                soundSynth.playGoldClink();
                this.showToast("Relic Added", data.message, "success");
                this.showNewRewardModal = false;
                this.newReward = { item_name: '', item_description: '', gold_cost: 50, icon_name: 'sparkles', item_type: 'IRL_REWARD' };
                await this.fetchHud();
            } catch (err) {
                this.showToast("Error", err.message, "error");
            } finally {
                this.creatingReward = false;
            }
        },

        // ----------------------------------------------------
        // PHASE VII: THE ORACLE (CELESTIAL DIVINATION & ASTROLABE)
        // ----------------------------------------------------
        async invokeProphecy() {
            this.prophecyLoading = true;
            try {
                soundSynth.playQuestComplete();
                const res = await fetch('/api/oracle/prophecy', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ inject_quests: true })
                });
                const data = await res.json();
                if (!res.ok) throw new Error(data.error || "Divination failed");

                soundSynth.playLevelUp();
                this.triggerConfetti(false);
                this.currentProphecy = data.prophecy;
                this.showToast("Celestial Decree Inscribed", `The Grand Astrolabe bestowed ${data.injected_quests_count} harmonic balance practices.`, "success");
                await this.fetchHud();
            } catch (err) {
                this.showToast("Divination Error", err.message, "error");
            } finally {
                this.prophecyLoading = false;
            }
        },

        // ----------------------------------------------------
        // CHART.JS CALM WUXIA / PAPER TELEMETRY RENDERERS
        // ----------------------------------------------------
        initCharts() {
            const radarCanvas = document.getElementById('radarChart');
            const velocityCanvas = document.getElementById('velocityChart');

            if (radarCanvas && window.Chart) {
                const ctx = radarCanvas.getContext('2d');
                this.radarChart = new Chart(ctx, {
                    type: 'radar',
                    data: {
                        labels: ['MIND (Spirit)', 'HEALTH (Physique)', 'CAREER (Dao)', 'WEALTH (Fortune)'],
                        datasets: [{
                            label: 'Pillar Qi',
                            data: [0, 0, 0, 0],
                            backgroundColor: 'rgba(15, 118, 110, 0.12)',
                            borderColor: '#0f766e', // Deep Celadon Jade
                            pointBackgroundColor: '#0f766e',
                            pointBorderColor: '#ffffff',
                            pointHoverBackgroundColor: '#ffffff',
                            pointHoverBorderColor: '#0f766e',
                            borderWidth: 2
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            r: {
                                angleLines: { color: 'rgba(120, 113, 108, 0.2)' },
                                grid: { color: 'rgba(120, 113, 108, 0.15)' },
                                pointLabels: {
                                    color: '#292524',
                                    font: { size: 11, weight: '600', family: 'Cinzel, serif' }
                                },
                                ticks: {
                                    backdropColor: 'transparent',
                                    color: '#78716c',
                                    showLabelBackdrop: false
                                }
                            }
                        },
                        plugins: {
                            legend: { display: false }
                        }
                    }
                });
            }

            if (velocityCanvas && window.Chart) {
                const ctx = velocityCanvas.getContext('2d');
                this.velocityChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: [],
                        datasets: [
                            {
                                label: 'Daily Qi Cultivated',
                                data: [],
                                yAxisID: 'yXP',
                                borderColor: '#0f766e', // Jade
                                backgroundColor: 'rgba(15, 118, 110, 0.08)',
                                tension: 0.35,
                                fill: true,
                                borderWidth: 2
                            },
                            {
                                label: 'Mind Harmony Score (-100 to 100)',
                                data: [],
                                yAxisID: 'ySentiment',
                                borderColor: '#b45309', // Sandalwood Amber
                                backgroundColor: 'transparent',
                                borderDash: [4, 4],
                                tension: 0.35,
                                borderWidth: 2
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        interaction: { mode: 'index', intersect: false },
                        scales: {
                            x: {
                                grid: { color: 'rgba(120, 113, 108, 0.08)' },
                                ticks: { color: '#57534e', font: { family: 'JetBrains Mono, monospace', size: 10 } }
                            },
                            yXP: {
                                type: 'linear',
                                position: 'left',
                                grid: { color: 'rgba(120, 113, 108, 0.08)' },
                                ticks: { color: '#0f766e', font: { family: 'JetBrains Mono, monospace', size: 10 } },
                                title: { display: true, text: 'Qi Gained', color: '#0f766e', font: { weight: '600' } }
                            },
                            ySentiment: {
                                type: 'linear',
                                position: 'right',
                                min: -100,
                                max: 100,
                                grid: { drawOnChartArea: false },
                                ticks: { color: '#b45309', font: { family: 'JetBrains Mono, monospace', size: 10 } },
                                title: { display: true, text: 'Mind Harmony', color: '#b45309', font: { weight: '600' } }
                            }
                        },
                        plugins: {
                            legend: {
                                labels: { color: '#292524', font: { family: 'Cinzel, serif', size: 11 } }
                            }
                        }
                    }
                });
            }

            this.updateCharts();
        },

        updateCharts() {
            if (this.radarChart && this.oracleData && this.oracleData.radar) {
                this.radarChart.data.labels = ['MIND (Spirit)', 'HEALTH (Physique)', 'CAREER (Dao)', 'WEALTH (Fortune)'];
                this.radarChart.data.datasets[0].data = this.oracleData.radar.values;
                this.radarChart.update();
            }

            if (this.velocityChart && this.oracleData && this.oracleData.velocity_14d) {
                this.velocityChart.data.labels = this.oracleData.velocity_14d.dates;
                this.velocityChart.data.datasets[0].data = this.oracleData.velocity_14d.xp;
                this.velocityChart.data.datasets[1].data = this.oracleData.velocity_14d.sentiment;
                this.velocityChart.update();
            }
        }
    };
}
