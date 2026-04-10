<template>
  <div v-if="visible" class="space-y-4">
    <div class="flex items-center justify-between text-sm">
      <span class="font-medium text-foreground">{{ currentStepLabel }}</span>
      <span class="text-muted-foreground">{{ pct }}%</span>
    </div>

    <!-- Progress bar -->
    <div class="h-2 bg-muted rounded-full overflow-hidden">
      <div
        class="h-full bg-primary rounded-full transition-all duration-500 ease-out"
        :style="{ width: pct + '%' }"
      />
    </div>

    <!-- Step indicators -->
    <div class="flex justify-between text-xs text-muted-foreground">
      <span
        v-for="step in displaySteps"
        :key="step.key"
        :class="step.active ? 'text-primary font-medium' : step.done ? 'text-foreground/60' : ''"
      >
        {{ step.label }}
      </span>
    </div>

    <!-- Error state -->
    <div v-if="errorMessage" class="rounded-md bg-destructive/10 border border-destructive/20 p-3">
      <p class="text-sm text-destructive">{{ errorMessage }}</p>
      <Button variant="outline" size="sm" class="mt-2" @click="emit('retry')">
        Try Again
      </Button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { Button } from '@/components/ui/button'
import type { UploadProgressEvent } from '@/services/api'

const props = defineProps<{
  currentEvent: UploadProgressEvent | null
  errorMessage: string
  hasPaper: boolean
}>()

const emit = defineEmits<{ retry: [] }>()

const pct = ref(0)
const currentStep = ref<string>('')

watch(
  () => props.currentEvent,
  event => {
    if (!event) return
    pct.value = event.pct
    currentStep.value = event.step
  },
)

const visible = computed(() => pct.value > 0 || props.errorMessage !== '')

const STEP_LABELS: Record<string, string> = {
  extracting: 'Extracting text',
  parsing_resume: 'Parsing resume',
  parsing_paper: 'Parsing paper',
  saving: 'Saving',
  done: 'Complete',
}

const displaySteps = computed(() => {
  const steps = ['extracting', 'parsing_resume']
  if (props.hasPaper) steps.push('parsing_paper')
  steps.push('saving', 'done')

  const currentIdx = steps.indexOf(currentStep.value)
  return steps.map((key, idx) => ({
    key,
    label: STEP_LABELS[key] ?? key,
    active: idx === currentIdx,
    done: idx < currentIdx,
  }))
})

const currentStepLabel = computed(() =>
  currentStep.value ? (STEP_LABELS[currentStep.value] ?? currentStep.value) : 'Preparing...',
)
</script>
