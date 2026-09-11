import random
import math

class DemocraticHammurabi:
    """
    Democratic Hammurabi with the Silver Shekel Monetary Economy.
    Decouples monetary capital (silver) from biological calories (grain).
    Features a dual-market economy:
    - Domestic Grain Market: Local supply/demand protects citizens from starvation.
    - Foreign Caravan Trade: 4-year deterministic world tariff schedule with merchant liquidity caps.
    """
    def __init__(self, max_years=12):
        self.max_years = max_years
        self.reset()

    def reset(self):
        self.year = 1
        self.population = 300
        self.grain = 6000             # Bushels of food & seed in royal silos
        self.land = 2500              # Acres of farmable land
        self.silver = 30000           # Silver shekels in royal vault
        self.elite_pop = int(self.population * 0.05)
        self.worker_pop = int(self.population * 0.15)
        self.farmer_pop = int(self.population * 0.80)

        self.civilian_grain = 6000    # Bushels in civilian granaries

        # Deterministic Foreign Caravan Price Schedule & Liquidity Caps
        self.caravan_price_cycle = [1.50, 2.20, 2.80, 1.20]
        self.caravan_silver_budget = 15000.0   # Foreign merchant purse per year
        self.caravan_cargo_capacity = 8000.0   # Max foreign grain available for import
        self.caravan_silver = float(self.caravan_silver_budget)
        self.caravan_cargo = float(self.caravan_cargo_capacity)

        self.update_demographics_and_prices()
        self.update_grain_price()

        # Dynamic wealth baseline
        self.initial_pop = self.population
        self.initial_wealth = self.silver + (self.land * self.land_price) + int(self.grain * self.grain_price)

        # Faction approvals (0 to 100)
        self.farmers_approval = 50.0
        self.workers_approval = 50.0
        self.elites_approval = 50.0

        # --- Civilian Monetary Balances (Closed-Loop Baseline) ---
        self.farmer_silver = float(self.farmer_pop * 50.0)    # 12,000 silver (50 / farmer)
        self.elite_silver = float(self.elite_pop * 500.0)     # 7,500 silver (500 / elite)
        self.worker_silver = float(self.worker_pop * 10.0)    # 450 silver (10 / worker)
        self.civilian_silver = self.farmer_silver + self.elite_silver + self.worker_silver
        self.elite_immigrant_pool = 0.0

        self.last_farmer_silver = float(self.farmer_silver)
        self.last_elite_silver = float(self.elite_silver)
        self.last_worker_silver = float(self.worker_silver)

        self.is_done = False
        self.game_over_reason = ""
        self.starved_total = 0
        self.last_rats_ate = 0
        self.last_harvest_yield = 5
        self.last_immigrants = 0
        self.last_silver = float(self.silver)
        self.last_land_price = float(self.land_price)

        # --- State Projects & Public Works ---
        self.active_project = 0
        self.project_name = "None"
        self.project_spent = 0.0
        self.canal_yield_bonus = 0
        self.granary_sealed = False
        self.reclaimed_land = 0
        self.last_civilian_grain_rot = 0
        self.last_is_feast = False
        self.last_feast_stimulus = 0
        self.social_mobility_events = []

        return self._get_state()

    def update_demographics_and_prices(self):
        self.population = self.elite_pop + self.farmer_pop + self.worker_pop
        self.land_demand = float(self.elite_pop * 20) + float(self.farmer_pop * 10) + float(self.worker_pop * 1)

        # Deterministic land price
        base_land_price = 25.0
        raw_land_price = base_land_price * (self.land_demand / max(1.0, float(self.land)))
        self.land_price = float(max(10.0, min(100.0, raw_land_price)))

    def update_grain_price(self):
        total_supply = float(self.grain + getattr(self, "civilian_grain", 0))
        total_demand = float(self.population * 20)

        # 1. Domestic Grain Price (Local bread price inside Babylon)
        raw_domestic_price = 1.0 * (total_demand / max(1.0, total_supply))
        self.domestic_grain_price = float(max(0.5, min(5.0, raw_domestic_price)))

        # 2. Foreign Caravan Price (Option 2: 4-Year Deterministic World Schedule)
        cycle_idx = (self.year - 1) % 4
        self.foreign_grain_price = float(self.caravan_price_cycle[cycle_idx])

        # Public market price is the foreign caravan price
        self.grain_price = self.foreign_grain_price

        # Annual caravan arrives with full purse and cargo budget
        self.caravan_silver = float(self.caravan_silver_budget)
        self.caravan_cargo = float(self.caravan_cargo_capacity)

    def _get_state(self):
        years_until_election = 4 - (self.year % 4)
        if years_until_election == 4:
            years_until_election = 0

        # 20-Dimensional State Vector (Full Markovian Observability)
        return [
            float(self.year),
            float(self.population),
            float(self.grain),
            float(self.land),
            float(self.land_price),
            float(self.silver),
            float(self.grain_price),
            float(self.farmers_approval),
            float(self.workers_approval),
            float(self.elites_approval),
            float(years_until_election),
            float(self.farmer_pop),
            float(self.worker_pop),
            float(self.elite_pop),
            float(self.civilian_grain),
            float(self.farmer_silver),
            float(self.elite_silver),
            float(self.worker_silver),
            float(self.domestic_grain_price),
            float(self.caravan_silver),
        ]

    def _build_info(self, **kwargs):
        info = {
            "reason": self.game_over_reason,
            "harvest_yield": kwargs.get("harvest_yield", self.last_harvest_yield),
            "rats_ate": kwargs.get("rats_ate", self.last_rats_ate),
            "immigrants": kwargs.get("immigrants", self.last_immigrants),
            "workers_starved": kwargs.get("workers_starved", 0),
            "civilians_starved": kwargs.get("civilians_starved", 0),
            "civilian_grain_bought": kwargs.get("civilian_grain_bought", 0),
            "harvest_total": kwargs.get("harvest_total", 0),
            "king_tax": kwargs.get("king_tax", 0),
            "civilian_harvest": kwargs.get("civilian_harvest", 0),
            "civilian_grain": self.civilian_grain,
            "domestic_grain_price": self.domestic_grain_price,
            "foreign_grain_price": self.foreign_grain_price,
            "caravan_silver": self.caravan_silver,
            "caravan_cargo": self.caravan_cargo,
            "civ_procured_grain": kwargs.get("civ_procured_grain", 0),
            "civ_procured_cost": kwargs.get("civ_procured_cost", 0),
            "caravan_grain_sold": kwargs.get("caravan_grain_sold", 0),
            "caravan_silver_earned": kwargs.get("caravan_silver_earned", 0),
            "caravan_grain_bought": kwargs.get("caravan_grain_bought", 0),
            "caravan_silver_spent": kwargs.get("caravan_silver_spent", 0),
            # --- Detailed Civilian Economy Debug Statistics ---
            "farmer_silver": self.farmer_silver,
            "elite_silver": self.elite_silver,
            "worker_silver": self.worker_silver,
            "civilian_silver": self.civilian_silver,
            "money_supply": float(self.silver + self.civilian_silver),
            "farmer_avg_silver": float(self.farmer_silver / max(1, self.farmer_pop)),
            "elite_avg_silver": float(self.elite_silver / max(1, self.elite_pop)),
            "worker_avg_silver": float(self.worker_silver / max(1, self.worker_pop)),
            "worker_wages_due": kwargs.get("worker_wages_due", float(self.worker_pop * 2.0)),
            "worker_wages_paid": kwargs.get("worker_wages_paid", 0.0),
            "worker_wages_unpaid": kwargs.get("worker_wages_unpaid", 0.0),
            "worker_market_spend": kwargs.get("worker_market_spend", 0.0),
            "civilian_grain_demand": kwargs.get("civilian_grain_demand", int((self.farmer_pop + self.elite_pop) * 20)),
            "civilian_grain_consumed": kwargs.get("civilian_grain_consumed", 0),
            "civilian_deficit": kwargs.get("civilian_deficit", 0),
            "civilian_silver_spent": kwargs.get("civilian_silver_spent", 0),
            "farmer_grain_sold": kwargs.get("farmer_grain_sold", 0),
            "farmer_silver_earned": kwargs.get("farmer_silver_earned", 0),
            "elite_profit": kwargs.get("elite_profit", 0),
            "land_changed": kwargs.get("land_changed", 0),
            "land_silver_transfer": kwargs.get("land_silver_transfer", 0),
            "immigrant_silver_brought": kwargs.get("immigrant_silver_brought", 0.0),
            "farmer_debt_distress": bool((self.farmer_silver / max(1, self.farmer_pop)) < 20.0),
            "elite_capital_flight": bool((self.elite_silver / max(1, self.elite_pop)) < 300.0),
            "active_project": self.active_project,
            "project_name": self.project_name,
            "project_spent": float(self.project_spent),
            "canal_yield_bonus": int(self.canal_yield_bonus),
            "granary_sealed": bool(self.granary_sealed),
            "reclaimed_land": int(self.reclaimed_land),
            "civilian_grain_rot": kwargs.get("civilian_grain_rot", self.last_civilian_grain_rot),
            "is_feast": bool(kwargs.get("is_feast", getattr(self, "last_is_feast", False))),
            "feast_stimulus": int(kwargs.get("feast_stimulus", getattr(self, "last_feast_stimulus", 0))),
            "social_mobility_events": list(self.social_mobility_events),
        }
        info.update(kwargs)
        return info

    def step(self, actions):
        """
        Actions can be:
        - 6 actions: [action_land, action_civ_procure, action_caravan_trade, action_feed, action_plant, action_project]
        - 5 actions: [action_land, action_caravan_trade, action_feed, action_plant, action_project]
        - 4 actions: [action_land, action_caravan_trade, action_feed, action_plant]
        """
        if self.is_done:
            return self._get_state(), 0, self.is_done, self._build_info(reason="Already done")

        action_land = float(actions[0])
        action_land = max(-1.0, min(1.0, action_land))

        if len(actions) >= 6:
            action_civ_procure = max(0.0, min(1.0, float(actions[1])))
            action_caravan_trade = max(-1.0, min(1.0, float(actions[2])))
            action_feed = max(0.0, min(1.0, float(actions[3])))
            action_plant = max(0.0, min(1.0, float(actions[4])))
            action_project = float(actions[5])
        elif len(actions) == 5:
            action_civ_procure = 0.0
            action_caravan_trade = max(-1.0, min(1.0, float(actions[1])))
            action_feed = max(0.0, min(1.0, float(actions[2])))
            action_plant = max(0.0, min(1.0, float(actions[3])))
            action_project = float(actions[4])
        else:
            action_civ_procure = 0.0
            action_caravan_trade = max(-1.0, min(1.0, float(actions[1])))
            action_feed = max(0.0, min(1.0, float(actions[2])))
            action_plant = max(0.0, min(1.0, float(actions[3])))
            action_project = 0.0

        # ----------------------------------------------------------------------
        # 1. Land Market (Closed-Loop Capital Transfer)
        # ----------------------------------------------------------------------
        land_changed = 0
        land_silver_transfer = 0
        if action_land < 0:
            # King sells land to civilians (capped by civilian purchasing power)
            intended_acres = int(round(abs(action_land) * self.land))
            total_civ_land_purse = self.farmer_silver + self.elite_silver
            max_civ_can_buy = int(total_civ_land_purse // self.land_price)
            acres_to_sell = min(intended_acres, max_civ_can_buy)

            if acres_to_sell > 0:
                cost = acres_to_sell * self.land_price
                self.land -= acres_to_sell
                self.silver += cost
                land_changed = -acres_to_sell
                land_silver_transfer = int(cost)

                # Deduct silver proportionally from private purses
                if total_civ_land_purse > 0:
                    f_ratio = self.farmer_silver / total_civ_land_purse
                    self.farmer_silver -= cost * f_ratio
                    self.elite_silver -= cost * (1.0 - f_ratio)
                self.civilian_silver = self.farmer_silver + self.elite_silver + self.worker_silver

        elif action_land > 0:
            # King buys land from private holders
            max_acres_affordable = int(self.silver // self.land_price)
            acres_to_buy = int(round(action_land * max_acres_affordable))

            if acres_to_buy > 0:
                cost = acres_to_buy * self.land_price
                self.land += acres_to_buy
                self.silver -= cost
                land_changed = acres_to_buy
                land_silver_transfer = -int(cost)

                # Transfer silver to private landholders (70% farmers, 30% elites)
                self.farmer_silver += cost * 0.70
                self.elite_silver += cost * 0.30
                self.civilian_silver = self.farmer_silver + self.elite_silver + self.worker_silver

        # ----------------------------------------------------------------------
        # 1b. State Worker Stipends & Elite Public Market
        # ----------------------------------------------------------------------
        worker_wage_cost = float(self.worker_pop * 2.0)
        if self.silver >= worker_wage_cost:
            worker_wages_paid = worker_wage_cost
            worker_wages_unpaid = 0.0
            self.silver -= worker_wages_paid
            self.worker_silver += worker_wages_paid
            self.workers_approval += 3.0
        else:
            worker_wages_paid = float(max(0.0, self.silver))
            worker_wages_unpaid = worker_wage_cost - worker_wages_paid
            unpaid_ratio = worker_wages_unpaid / max(1.0, worker_wage_cost)
            self.silver = 0.0
            self.worker_silver += worker_wages_paid
            self.workers_approval -= 12.0 * unpaid_ratio

        # Workers spend silver in Elite-run Public Market for bread & artisan goods
        worker_market_spend = min(self.worker_silver, float(self.worker_pop * 1.5))
        self.worker_silver -= worker_market_spend
        self.elite_silver += worker_market_spend
        self.civilian_silver = self.farmer_silver + self.elite_silver + self.worker_silver

        # ----------------------------------------------------------------------
        # 1c. State Projects & Infrastructure (Keynesian Multiplier)
        # ----------------------------------------------------------------------
        project_choice = 0
        if action_project >= 1.0:
            project_choice = int(round(action_project))
        elif action_project > 0.25:
            if action_project <= 0.50:
                project_choice = 1
            elif action_project <= 0.75:
                project_choice = 2
            else:
                project_choice = 3

        self.active_project = 0
        self.project_name = "None"
        self.project_spent = 0.0
        self.canal_yield_bonus = 0
        self.granary_sealed = False
        self.reclaimed_land = 0

        if project_choice == 1:
            # 1. Canal Dredging & Silt Clearing (Pattum): 500 silver, >= 30 workers
            cost = 500.0
            if self.silver >= cost and self.worker_pop >= 30:
                self.silver -= cost
                self.project_spent = cost
                self.active_project = 1
                self.project_name = "Canal Dredging"
                self.canal_yield_bonus = random.randint(1, 2)
                # Keynesian labor dividend: 20% distributed to workers
                self.worker_silver += cost * 0.20
                self.workers_approval += 4.0
                self.farmers_approval += 5.0

        elif project_choice == 2:
            # 2. Granary Bitumen Fortification (Qiru): 400 silver, >= 20 workers
            cost = 400.0
            if self.silver >= cost and self.worker_pop >= 20:
                self.silver -= cost
                self.project_spent = cost
                self.active_project = 2
                self.project_name = "Granary Fortification"
                self.granary_sealed = True
                self.worker_silver += cost * 0.20
                self.workers_approval += 2.0
                self.elites_approval += 3.0

        elif project_choice == 3:
            # 3. Marsh Drainage & Land Reclamation (A.GAR): 600 silver, >= 35 workers
            cost = 600.0
            if self.silver >= cost and self.worker_pop >= 35:
                self.silver -= cost
                self.project_spent = cost
                self.active_project = 3
                self.project_name = "Land Reclamation"
                reclaimed = random.randint(60, 100)
                self.land += reclaimed
                self.reclaimed_land = reclaimed
                self.worker_silver += cost * 0.20
                self.workers_approval += 4.0
                self.farmers_approval += 4.0

        self.civilian_silver = self.farmer_silver + self.elite_silver + self.worker_silver

        # ----------------------------------------------------------------------
        # 2a. Domestic Grain Procurement (Peasant Granary Wholesale)
        # ----------------------------------------------------------------------
        civ_procured_grain = 0
        civ_procured_cost = 0
        civ_safe_reserve = (self.farmer_pop + self.elite_pop) * 40
        civ_surplus = max(0, self.civilian_grain - civ_safe_reserve)

        if action_civ_procure > 0 and civ_surplus > 0 and self.silver >= self.domestic_grain_price:
            max_king_can_afford = int(self.silver // self.domestic_grain_price)
            intended_procure = int(round(action_civ_procure * min(civ_surplus, max_king_can_afford)))
            bushels_to_buy = min(intended_procure, civ_surplus, max_king_can_afford)

            if bushels_to_buy > 0:
                cost = int(bushels_to_buy * self.domestic_grain_price)
                self.silver -= cost
                self.farmer_silver += cost
                self.grain += bushels_to_buy
                self.civilian_grain -= bushels_to_buy
                self.civilian_silver = self.farmer_silver + self.elite_silver + self.worker_silver
                civ_procured_grain = bushels_to_buy
                civ_procured_cost = cost

        # ----------------------------------------------------------------------
        # 2b. Foreign Caravan Trade (Merchant Export / Import)
        # ----------------------------------------------------------------------
        caravan_grain_sold = 0
        caravan_silver_earned = 0
        caravan_grain_bought = 0
        caravan_silver_spent = 0
        grain_traded = 0

        if action_caravan_trade < 0:
            # Export royal grain for foreign silver! CAPPED by caravan silver purse!
            max_caravan_can_buy = int(self.caravan_silver // self.grain_price)
            intended_export = int(round(abs(action_caravan_trade) * self.grain))
            bushels_to_sell = min(intended_export, max_caravan_can_buy)

            if bushels_to_sell > 0:
                silver_earned = int(bushels_to_sell * self.grain_price)
                self.grain -= bushels_to_sell
                self.silver += silver_earned
                self.caravan_silver -= silver_earned
                caravan_grain_sold = bushels_to_sell
                caravan_silver_earned = silver_earned
                grain_traded = -bushels_to_sell

        elif action_caravan_trade > 0:
            # Import foreign grain with royal silver! CAPPED by caravan cargo!
            max_king_can_afford = int(self.silver // self.grain_price)
            intended_import = int(round(action_caravan_trade * max_king_can_afford))
            bushels_to_buy = min(intended_import, int(self.caravan_cargo))

            if bushels_to_buy > 0:
                silver_spent = int(bushels_to_buy * self.grain_price)
                self.grain += bushels_to_buy
                self.silver -= silver_spent
                self.caravan_cargo -= bushels_to_buy
                caravan_grain_bought = bushels_to_buy
                caravan_silver_spent = silver_spent
                grain_traded = bushels_to_buy

        # ----------------------------------------------------------------------
        # 3. Feeding Citizens (Workers & Civilians)
        # ----------------------------------------------------------------------
        # Feeding state workers from royal grain (round to prevent float truncation, e.g. 899.999 -> 900)
        grain_for_food = int(round(action_feed * self.grain))
        self.grain -= grain_for_food

        workers_fed = grain_for_food // 20
        workers_starved = max(0, self.worker_pop - workers_fed)
        # Check if the King hosted a Grand Feast (>= 24 bushels/worker, i.e. 120%+ of standard rations)
        is_feast = bool(self.worker_pop > 0 and workers_starved == 0 and (grain_for_food >= int(self.worker_pop * 24)))
        self.last_is_feast = is_feast

        # Update domestic market grain price before civilian purchases occur
        total_supply = float(self.grain + getattr(self, "civilian_grain", 0))
        total_demand = float(self.population * 20)
        raw_domestic_price = 1.0 * (total_demand / max(1.0, total_supply))
        self.domestic_grain_price = float(max(0.5, min(5.0, raw_domestic_price)))

        # Civilian food requirements (Farmers + Elites)
        total_civilians = self.elite_pop + self.farmer_pop
        civilian_food_demand = total_civilians * 20

        # Civilians eat available civilian granary reserves first
        grain_consumed = min(self.civilian_grain, civilian_food_demand)
        self.civilian_grain -= grain_consumed
        civilian_deficit = civilian_food_demand - grain_consumed

        civilians_starved = 0
        civilian_grain_bought = 0
        civilian_silver_spent = 0

        if civilian_deficit > 0:
            # Solvency check: Civilians can only buy what their private silver can afford!
            total_civ_purse = self.farmer_silver + self.elite_silver
            max_affordable_bushels = int(total_civ_purse // self.domestic_grain_price)

            # Civilians purchase what they can afford from royal silos
            civilian_grain_bought = min(civilian_deficit, max_affordable_bushels, self.grain)
            civilian_silver_spent = int(civilian_grain_bought * self.domestic_grain_price)

            self.grain -= civilian_grain_bought
            self.silver += civilian_silver_spent

            # Deduct silver proportionally from private purses
            if total_civ_purse > 0:
                f_ratio = self.farmer_silver / total_civ_purse
                self.farmer_silver -= civilian_silver_spent * f_ratio
                self.elite_silver -= civilian_silver_spent * (1.0 - f_ratio)
            self.civilian_silver = self.farmer_silver + self.elite_silver + self.worker_silver

            # Any remaining shortfall results directly in real starvation (20 bu/person)
            unmet_deficit = civilian_deficit - civilian_grain_bought
            civilians_starved = min(total_civilians, unmet_deficit // 20)

        starved = workers_starved + civilians_starved
        self.starved_total = starved

        if starved > 0:
            if workers_starved > 0:
                self.worker_pop = max(0, self.worker_pop - workers_starved)
            if civilians_starved > 0:
                total_civ = max(1, self.farmer_pop + self.elite_pop)
                f_starved = min(self.farmer_pop, int(round(civilians_starved * (self.farmer_pop / total_civ))))
                e_starved = min(self.elite_pop, civilians_starved - f_starved)
                self.farmer_pop -= f_starved
                self.elite_pop -= e_starved
            self.population = self.farmer_pop + self.worker_pop + self.elite_pop
            self.update_demographics_and_prices()

        # Immediate impeachment if starvation exceeds 45%
        if starved > 0.45 * (self.population + starved):
            self.is_done = True
            self.game_over_reason = "Impeached for extreme starvation"
            return self._get_state(), self._calculate_reward(), self.is_done, self._build_info(
                reason=self.game_over_reason,
                workers_starved=workers_starved,
                civilians_starved=civilians_starved,
                civilian_grain_bought=civilian_grain_bought,
                civilian_silver_spent=civilian_silver_spent,
                civilian_grain_demand=int(civilian_food_demand),
                civilian_grain_consumed=int(grain_consumed),
                civilian_deficit=int(civilian_deficit),
                worker_wages_due=float(worker_wage_cost),
                worker_wages_paid=float(worker_wages_paid),
                worker_wages_unpaid=float(worker_wages_unpaid),
                worker_market_spend=float(worker_market_spend),
                land_changed=int(land_changed),
                land_silver_transfer=int(land_silver_transfer),
            )

        # ----------------------------------------------------------------------
        # 4. Planting Seeds (1 bushel per acre, max 10 acres per farmer)
        # ----------------------------------------------------------------------
        grain_for_planting = int(round(action_plant * self.grain))
        max_workable_by_people = self.farmer_pop * 10
        actual_planted = min(grain_for_planting, self.land, max_workable_by_people)
        self.grain -= actual_planted

        # ----------------------------------------------------------------------
        # 5. Harvest & Rats
        # ----------------------------------------------------------------------
        yield_cycle = [5, 8, 3, 13]
        yield_per_acre = yield_cycle[(self.year - 1) % 4]
        effective_yield = yield_per_acre + self.canal_yield_bonus
        self.last_harvest_yield = effective_yield

        harvest = actual_planted * effective_yield

        # 40% Tax goes to king, 60% stays with civilian producers
        king_tax = int(harvest * 0.4)
        civilian_harvest = harvest - king_tax

        self.grain += king_tax
        self.civilian_grain += civilian_harvest

        # ----------------------------------------------------------------------
        # 5b. Agrarian Surplus Monetization & Elite Market Operations
        # ----------------------------------------------------------------------
        # Farmers sell surplus grain (beyond baseline family need) to Elites at domestic rate.
        # Elites purchase grain as wholesale inventory and resell in the public market at retail margin.
        farmer_food_need = self.farmer_pop * 20
        farmer_grain_sold = 0
        farmer_silver_earned = 0
        retail_margin = 0
        if self.civilian_grain > farmer_food_need:
            urban_demand = (self.worker_pop + self.elite_pop) * 20
            surplus_bushels = min(int((self.civilian_grain - farmer_food_need) * 0.50), urban_demand)
            surplus_cost = int(surplus_bushels * self.domestic_grain_price)

            # Elites allocate up to 25% of their working capital for grain inventory
            max_elite_trading_budget = int(self.elite_silver * 0.25)
            actual_cost = min(surplus_cost, max_elite_trading_budget)

            if self.domestic_grain_price > 0 and actual_cost > 0:
                actual_bushels = int(actual_cost // self.domestic_grain_price)
                # Farmers receive full payment for their grain
                self.farmer_silver += actual_cost
                farmer_grain_sold = actual_bushels
                farmer_silver_earned = actual_cost

                # Elites retail processed bread/goods in public market at a 30% commercial markup
                retail_margin = int(actual_cost * 0.30)
                self.elite_silver += retail_margin

                # Purchased surplus grain is consumed / retailed out of civilian farm silos
                self.civilian_grain -= actual_bushels

        # Elite Commercial Dividend (Caravan merchant finance & private estate rents)
        land_rents = int(self.elite_pop * (self.land_price * 0.80))
        caravan_commission = int(abs(grain_traded) * self.grain_price * 0.05)
        elite_profit = land_rents + caravan_commission
        self.elite_silver += elite_profit
        self.civilian_silver = self.farmer_silver + self.elite_silver + self.worker_silver

        # Rats: random chance of infestation with variable severity (blocked if granary_sealed!)
        rats_ate = 0
        if not self.granary_sealed:
            if self.grain > 5000 and random.random() <= 0.40:
                severity = random.uniform(0.05, 0.15)  # 5-15% of royal grain
                rats_ate = int(self.grain * severity)
                self.grain -= rats_ate
        self.last_rats_ate = rats_ate

        # ----------------------------------------------------------------------
        # 5d. Pop-Adjusted 2-Year Strategic Reserve & Civilian Granary Spoilage
        # ----------------------------------------------------------------------
        civ_safe_reserve = (self.farmer_pop + self.elite_pop) * 40
        civ_rot = 0
        if self.civilian_grain > civ_safe_reserve:
            excess_grain = self.civilian_grain - civ_safe_reserve
            civ_rot = int(excess_grain * random.uniform(0.10, 0.20))
            self.civilian_grain -= civ_rot
        self.last_civilian_grain_rot = civ_rot

        # ----------------------------------------------------------------------
        # 6. Demographics (Births & Immigrants)
        # ----------------------------------------------------------------------
        immigrants = 0
        immigrant_silver_brought = 0.0
        feast_stimulus = 0
        if starved == 0:
            wealth_factor = (20 * self.land + self.grain + self.silver) / (100 * self.population + 1)
            # Keynesian Stimulus: Public capital investments attract additional settlers
            project_stimulus = int((self.project_spent / 500.0) * 2) if self.project_spent > 0 else 0
            # Feast Attractiveness: Word of Babylon's grand feasts & abundance attracts extra settlers!
            feast_stimulus = random.randint(3, 7) if is_feast else 0
            self.last_feast_stimulus = feast_stimulus
            immigrants = 5 + int(wealth_factor) + project_stimulus + feast_stimulus

            # Immigrant Wealth Influx (Approach A): New settlers bring personal savings
            self.elite_immigrant_pool += immigrants * 0.05
            new_elites = int(self.elite_immigrant_pool)
            self.elite_immigrant_pool -= new_elites
            new_farmers = int(round(immigrants * 0.80))
            new_workers = max(0, immigrants - new_farmers - new_elites)

            self.farmer_pop += new_farmers
            self.elite_pop += new_elites
            self.worker_pop += new_workers
            self.population = self.farmer_pop + self.elite_pop + self.worker_pop
            self.update_demographics_and_prices()

            imm_f_silver = new_farmers * 50.0
            imm_e_silver = new_elites * 500.0
            imm_w_silver = new_workers * 10.0
            immigrant_silver_brought = imm_f_silver + imm_e_silver + imm_w_silver

            self.farmer_silver += imm_f_silver
            self.elite_silver += imm_e_silver
            self.worker_silver += imm_w_silver
            self.civilian_silver = self.farmer_silver + self.elite_silver + self.worker_silver

        self.last_immigrants = immigrants

        # ----------------------------------------------------------------------
        # 6b. Dynamic Social Mobility
        # ----------------------------------------------------------------------
        self.social_mobility_events = []

        # 1. Homesteading (Worker -> Farmer): Unworked land exists & worker has savings
        unworked_land = max(0, self.land - (self.farmer_pop * 10))
        w_avg = self.worker_silver / max(1, self.worker_pop)
        if unworked_land >= 10 and w_avg >= 15.0 and self.worker_pop > 10:
            settlers = min(2, unworked_land // 10, self.worker_pop - 10)
            if settlers > 0:
                silver_transfer = settlers * w_avg
                self.worker_pop -= settlers
                self.farmer_pop += settlers
                self.worker_silver -= silver_transfer
                self.farmer_silver += silver_transfer
                self.social_mobility_events.append(f"{settlers} worker(s) homesteaded to become farmer(s)")

        # 2. Merchant Ennoblement (Farmer -> Elite): Wealthy farmers buy urban stalls
        f_avg = self.farmer_silver / max(1, self.farmer_pop)
        if f_avg >= 90.0 and self.farmer_pop > 50:
            ennobled = 1
            silver_transfer = ennobled * f_avg
            self.farmer_pop -= ennobled
            self.elite_pop += ennobled
            self.farmer_silver -= silver_transfer
            self.elite_silver += silver_transfer
            self.social_mobility_events.append("1 wealthy farmer family joined the Elite merchant council")

        # 3. Proletarianization (Farmer -> Worker): Land shortage or peasant debt distress
        land_deficit = (self.farmer_pop * 10) - self.land
        if (f_avg < 20.0 or land_deficit > 100) and self.farmer_pop > 50:
            demoted = 1
            silver_transfer = min(self.farmer_silver, demoted * f_avg)
            self.farmer_pop -= demoted
            self.worker_pop += demoted
            self.farmer_silver -= silver_transfer
            self.worker_silver += silver_transfer
            self.social_mobility_events.append("1 landless peasant took up state wage labor")

        # 4. Fallen House (Elite -> Farmer): Bankrupt patricians sell estates
        e_avg = self.elite_silver / max(1, self.elite_pop)
        if e_avg < 250.0 and self.elite_pop > 5:
            fallen = 1
            silver_transfer = min(self.elite_silver, fallen * e_avg)
            self.elite_pop -= fallen
            self.farmer_pop += fallen
            self.elite_silver -= silver_transfer
            self.farmer_silver += silver_transfer
            self.social_mobility_events.append("1 bankrupt Elite house returned to common farming")

        self.population = self.farmer_pop + self.elite_pop + self.worker_pop
        self.civilian_silver = self.farmer_silver + self.elite_silver + self.worker_silver
        self.update_demographics_and_prices()

        # ----------------------------------------------------------------------
        # 7. Faction Approval Updates
        # ----------------------------------------------------------------------
        if land_changed > 0:
            self.farmers_approval += 5
        elif land_changed < 0:
            self.farmers_approval -= 10
        if actual_planted == self.land:
            self.farmers_approval += 5
        if civilians_starved > 0:
            self.farmers_approval -= 20

        if workers_starved > 0:
            self.workers_approval -= (workers_starved / max(1, self.worker_pop)) * 100
        elif is_feast:
            # Grand Royal Feast: Generous rations surge worker popularity and spread festive spirit!
            self.workers_approval += 12.0
            self.farmers_approval += 3.0
            self.social_mobility_events.append(f"Grand Royal Feast held! (+12% Worker Approval, +{feast_stimulus} Immigrants)")
        else:
            self.workers_approval += 5

        if self.silver >= self.last_silver:
            self.elites_approval += 3
        else:
            self.elites_approval -= 5

        if self.land_price >= self.last_land_price:
            self.elites_approval += 2
        else:
            self.elites_approval -= 2

        # Financial Health & Solvency Feedback Loops
        farmer_avg = self.farmer_silver / max(1, self.farmer_pop)
        if farmer_avg < 20.0:
            self.farmers_approval -= 3.0  # Debt distress
        elif farmer_avg >= 50.0:
            self.farmers_approval += 2.0  # Agrarian prosperity

        elite_avg = self.elite_silver / max(1, self.elite_pop)
        if elite_avg < 300.0:
            self.elites_approval -= 3.0   # Capital flight / market stagnation
        elif elite_avg >= 500.0:
            self.elites_approval += 2.0   # Commercial boom

        self.last_silver = self.silver
        self.last_land_price = self.land_price

        self.farmers_approval = self._clamp_and_decay_approval(self.farmers_approval)
        self.workers_approval = self._clamp_and_decay_approval(self.workers_approval)
        self.elites_approval = self._clamp_and_decay_approval(self.elites_approval)

        # ----------------------------------------------------------------------
        # 8. Democratic Elections (Every 4 years)
        # ----------------------------------------------------------------------
        if self.year % 4 == 0:
            average_approval = self.get_average_approval()
            if average_approval < 45.0:
                self.is_done = True
                self.game_over_reason = f"Lost election with {average_approval:.1f}% approval"
                return self._get_state(), self._calculate_reward(), self.is_done, self._build_info(
                    reason=self.game_over_reason,
                    harvest_yield=effective_yield,
                    rats_ate=rats_ate,
                    immigrants=immigrants,
                    workers_starved=workers_starved,
                    civilians_starved=civilians_starved,
                    civilian_grain_bought=civilian_grain_bought,
                    civ_procured_grain=int(civ_procured_grain),
                    civ_procured_cost=int(civ_procured_cost),
                    caravan_grain_sold=int(caravan_grain_sold),
                    caravan_silver_earned=int(caravan_silver_earned),
                    caravan_grain_bought=int(caravan_grain_bought),
                    caravan_silver_spent=int(caravan_silver_spent),
                    civilian_grain_rot=int(civ_rot),
                    harvest_total=harvest,
                    king_tax=king_tax,
                    civilian_harvest=civilian_harvest,
                    worker_wages_due=float(worker_wage_cost),
                    worker_wages_paid=float(worker_wages_paid),
                    worker_wages_unpaid=float(worker_wages_unpaid),
                    worker_market_spend=float(worker_market_spend),
                    civilian_grain_demand=int(civilian_food_demand),
                    civilian_grain_consumed=int(grain_consumed),
                    civilian_deficit=int(civilian_deficit),
                    civilian_silver_spent=int(civilian_silver_spent),
                    farmer_grain_sold=int(farmer_grain_sold),
                    farmer_silver_earned=int(farmer_silver_earned),
                    elite_profit=int(elite_profit),
                    land_changed=int(land_changed),
                    land_silver_transfer=int(land_silver_transfer),
                    immigrant_silver_brought=float(immigrant_silver_brought),
                )

        # ----------------------------------------------------------------------
        # 9. Next Year Market Price Fluctuations
        # ----------------------------------------------------------------------
        self.year += 1
        self.update_demographics_and_prices()
        self.update_grain_price()

        if self.year > self.max_years:
            self.is_done = True
            self.game_over_reason = "Completed term successfully!"

        return self._get_state(), self._calculate_reward(), self.is_done, self._build_info(
            reason=self.game_over_reason,
            harvest_yield=effective_yield,
            rats_ate=rats_ate,
            immigrants=immigrants,
            workers_starved=workers_starved,
            civilians_starved=civilians_starved,
            civilian_grain_bought=civilian_grain_bought,
            civ_procured_grain=int(civ_procured_grain),
            civ_procured_cost=int(civ_procured_cost),
            caravan_grain_sold=int(caravan_grain_sold),
            caravan_silver_earned=int(caravan_silver_earned),
            caravan_grain_bought=int(caravan_grain_bought),
            caravan_silver_spent=int(caravan_silver_spent),
            civilian_grain_rot=int(civ_rot),
            harvest_total=harvest,
            king_tax=king_tax,
            civilian_harvest=civilian_harvest,
            worker_wages_due=float(worker_wage_cost),
            worker_wages_paid=float(worker_wages_paid),
            worker_wages_unpaid=float(worker_wages_unpaid),
            worker_market_spend=float(worker_market_spend),
            civilian_grain_demand=int(civilian_food_demand),
            civilian_grain_consumed=int(grain_consumed),
            civilian_deficit=int(civilian_deficit),
            civilian_silver_spent=int(civilian_silver_spent),
            farmer_grain_sold=int(farmer_grain_sold),
            farmer_silver_earned=int(farmer_silver_earned),
            retail_margin=int(retail_margin),
            elite_profit=int(elite_profit),
            land_changed=int(land_changed),
            land_silver_transfer=int(land_silver_transfer),
            immigrant_silver_brought=float(immigrant_silver_brought),
        )

    def get_average_approval(self):
        total_voters = max(1, self.farmer_pop + self.worker_pop + self.elite_pop)
        average_approval = ((self.farmer_pop * self.farmers_approval) +
                            (self.worker_pop * self.workers_approval) +
                            (self.elite_pop * self.elites_approval)) / total_voters
        return average_approval

    def _clamp_and_decay_approval(self, approval):
        if approval > 50:
            approval -= (approval - 50) * 0.1
        elif approval < 50:
            approval += (50 - approval) * 0.1
        return max(0.0, min(100.0, approval))

    def _calculate_reward(self):
        survival_bonus = self.year * 100
        wealth_score = (self.silver + (self.land * self.land_price) + (self.grain * self.grain_price)) / 100.0
        pop_score = self.population * 2
        approval_score = min(self.farmers_approval, self.workers_approval, self.elites_approval) * 3.0
        penalty = self.starved_total * 50

        total_score = survival_bonus + wealth_score + pop_score + approval_score - penalty

        if self.is_done and self.year <= self.max_years:
            total_score = total_score / 10.0

        return total_score
