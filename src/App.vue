<script setup lang="ts">
import {
	NH1,
	NSwitch,
	NSelect,
	NSpace,
	NH2,
	NTag,
} from "naive-ui";

interface MenuDefinition {
	name: string;
	image: string;
	type: "sandwich" | "plate" | "other";
	contents: string[];
	notes: string;
	prices: Record<string, number>;
}

import menuJson from "../menu.json";
import { computed, ref } from "vue";

const menuDefinition: MenuDefinition[] = menuJson as any;

function setContainedWithin(needles: Set<unknown>, haystack: Set<unknown>) {
	for (const item of needles) {
		if (!haystack.has(item)) {
			return false;
		}
	}
	return true;
}

function extractContentOptions(menu: MenuDefinition[]) {
	const options: Record<string, Set<string>> = {
		sandwich: new Set<string>(),
		plate: new Set<string>(),
	}

	for (const item of menu) {
		if (item.type in options) {
			for (const c of item.contents) {
				options[item.type].add(c);
			}
		}
	}

	return options;
}

interface MenuItem {
	name: string;
	contents: Set<string>;
	prices: Record<string, number>;
	image: string;
	notes: string;
}

function createMenuTree(menu: MenuDefinition[]) {
	const tree: Record<string, MenuItem[]> = {
		sandwich: [],
		plate: [],
		other: [],
	}

	for (const item of menu) {
		if (item.type in tree) {
			tree[item.type].push({
				name: item.name,
				contents: new Set(item.contents),
				prices: item.prices,
				image: item.image,
				notes: item.notes,
			});
		}
	}

	return tree;
}

// function priceString(prices: Record<string, number>) {
// 	let result: string[] = [];
// 	for (const priceName in prices) {
// 		if (priceName != "base") {
// 			result.push(`${priceName}: ${prices[priceName]}€`);
// 		} else {
// 			result.push(`${prices[priceName]}€`);
// 		}
// 	}
// 	return result.join(" | ");
// }

const styleOptions = [
	{
		label: "Teller",
		value: "plate",
	},
	{
		label: "Sandwich",
		value: "sandwich",
	},
	{
		label: "Anderes",
		value: "other",
	}
];
const selectedStyle = ref<string>("sandwich");

const contentOptions = extractContentOptions(menuDefinition);
const selectedOptions = ref<Set<string>>(new Set());
const menuTree = createMenuTree(menuDefinition);

const suggestedOptions = computed<MenuItem[]>(() => {
	if (!(selectedStyle.value in menuTree)) {
		return [];
	}

	const menuOptions = menuTree[selectedStyle.value];
	const result: MenuItem[] = [];

	for (const option of menuOptions) {
		if (setContainedWithin(selectedOptions.value, option.contents)) {
			result.push(option);
		}
	}

	return result;
});

</script>

<template>
	<main>
		<n-h1>Anya Konfigurator</n-h1>

		<n-select
			:options="styleOptions"
			v-model:value="selectedStyle"
			@update:value="selectedOptions.clear()"
		/>

		<n-h2 v-if="selectedStyle in contentOptions">Optionen</n-h2>

		<n-space v-if="selectedStyle in contentOptions" :wrap="true">
			<n-space v-for="option in contentOptions[selectedStyle]" :key="option">
				<n-switch					
					:value="selectedOptions.has(option)"
					:on-update:value="val => { if (val) selectedOptions.add(option); else selectedOptions.delete(option); }"
				/>
				{{ option }}
			</n-space>
		</n-space>

		<n-h2>Treffer</n-h2>

		<n-space vertical>
			<div v-for="option in suggestedOptions" :key="option.name">
				<div style="margin-bottom: 5px">
					<b>{{ option.name }}</b>
					<!-- <span class="prices">{{ priceString(option.prices) }}</span> -->
					<span class="prices" v-for="(price, priceName) in option.prices" :key="priceName">
						{{ (priceName != "base") ? priceName + ":" : ""}} {{ price }}€
					</span>
				</div>
				<div>{{  option.notes }}</div>
				<n-space>
					<n-tag 
						v-for="content in [...option.contents].sort()"
						:key="content"
						size="small"
						:type="selectedOptions.has(content) ? 'success' : 'default'"
					>
						{{ content }}
					</n-tag>
				</n-space>
			</div>
		</n-space>
	</main>
</template>

<style scoped>
main {
	padding: 20px;
	max-width: 800px;
}

.prices {
	background-color: #77DD77;
	margin-left: 5px;
	padding: 0 10px;
	font-style: italic;
	border-radius: 5px;
}
</style>
