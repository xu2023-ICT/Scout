<script setup lang="ts">
import { useField } from 'vee-validate'

const props = defineProps<{
  name: string
}>()

const { value, errorMessage, handleChange, handleBlur } = useField(() => props.name)

const field = {
  get value() { return value.value },
  onChange: handleChange,
  onBlur: handleBlur,
}
</script>

<template>
  <slot :field="field" :errorMessage="errorMessage" />
</template>
