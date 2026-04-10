<template>
  <form @submit.prevent="handleSave" class="space-y-6">
    <PersonalSection />
    <EducationSection />
    <WorkSection />
    <SkillsSection />
    <ProjectsSection />
    <PaperSection v-if="hasPaper" />

    <div class="flex gap-3 pt-4 border-t sticky bottom-0 bg-background py-4">
      <Button type="submit" :disabled="isSaving || isConfirmed">
        {{ isSaving ? 'Saving...' : 'Save Changes' }}
      </Button>
      <Button
        type="button"
        variant="default"
        :disabled="isConfirmed || isSaving"
        @click="handleConfirm"
      >
        {{ isConfirmed ? 'Confirmed' : 'Confirm & Proceed' }}
      </Button>
      <Badge v-if="isConfirmed" variant="secondary" class="ml-auto self-center">
        Data confirmed — ready for job search
      </Badge>
    </div>
  </form>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useForm } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import { z } from 'zod'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { useResumeStore } from '@/stores/resume'
import PersonalSection from './PersonalSection.vue'
import EducationSection from './EducationSection.vue'
import WorkSection from './WorkSection.vue'
import SkillsSection from './SkillsSection.vue'
import ProjectsSection from './ProjectsSection.vue'
import PaperSection from './PaperSection.vue'

const resumeStore = useResumeStore()
const isSaving = ref(false)
const hasPaper = computed(() => !!resumeStore.paperData)
const isConfirmed = computed(() => resumeStore.isConfirmed)

// Zod schema mirrors ParsedResume — all optional to allow partial edits (D-07)
const resumeSchema = z.object({
  personal: z.object({
    name: z.string().min(1, 'Name is required'),
    email: z.string(),
    phone: z.string(),
    location: z.string(),
    linkedin: z.string(),
    github: z.string(),
    website: z.string(),
    summary: z.string(),
  }),
  education: z.array(z.object({
    institution: z.string(),
    degree: z.string(),
    field: z.string(),
    start_date: z.string(),
    end_date: z.string(),
    gpa: z.string(),
    description: z.string(),
  })),
  work_experience: z.array(z.object({
    company: z.string(),
    title: z.string(),
    start_date: z.string(),
    end_date: z.string(),
    location: z.string(),
    bullets: z.array(z.string()),
  })),
  projects: z.array(z.object({
    name: z.string(),
    description: z.string(),
    technologies: z.array(z.string()),
    url: z.string(),
    bullets: z.array(z.string()),
  })),
  skills: z.object({
    languages: z.array(z.string()),
    frameworks: z.array(z.string()),
    tools: z.array(z.string()),
    other: z.array(z.string()),
  }),
})

const { handleSubmit, resetForm } = useForm({
  validationSchema: toTypedSchema(resumeSchema),
  initialValues: resumeStore.parsedData ?? undefined,
})

// Watch for store data to arrive (in case form mounts before store loads)
watch(() => resumeStore.parsedData, (data) => {
  if (data) resetForm({ values: data as any })
}, { immediate: true })

const handleSave = handleSubmit(async (values) => {
  isSaving.value = true
  try {
    await resumeStore.saveEdits(values as any)
  } finally {
    isSaving.value = false
  }
})

async function handleConfirm() {
  // Save first, then confirm
  isSaving.value = true
  try {
    const currentValues = resumeStore.parsedData
    if (currentValues) await resumeStore.saveEdits(currentValues)
    await resumeStore.confirmResume()
  } finally {
    isSaving.value = false
  }
}
</script>
