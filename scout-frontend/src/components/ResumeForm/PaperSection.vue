<template>
  <Card>
    <CardHeader>
      <CardTitle>Academic Paper</CardTitle>
      <p class="text-sm text-muted-foreground">Extracted from your uploaded paper PDF</p>
    </CardHeader>
    <CardContent class="space-y-4" v-if="paperData">
      <div class="grid grid-cols-2 gap-4">
        <div class="col-span-2 space-y-1">
          <Label class="text-sm font-medium">Title</Label>
          <p class="text-sm border rounded-md px-3 py-2 bg-muted/30">{{ paperData.title || '—' }}</p>
        </div>
        <div class="space-y-1">
          <Label class="text-sm font-medium">Authors</Label>
          <p class="text-sm border rounded-md px-3 py-2 bg-muted/30">{{ paperData.authors.join(', ') || '—' }}</p>
        </div>
        <div class="space-y-1">
          <Label class="text-sm font-medium">Venue</Label>
          <p class="text-sm border rounded-md px-3 py-2 bg-muted/30">{{ paperData.venue || '—' }}</p>
        </div>
        <div class="space-y-1">
          <Label class="text-sm font-medium">Year</Label>
          <p class="text-sm border rounded-md px-3 py-2 bg-muted/30">{{ paperData.year || '—' }}</p>
        </div>
        <div class="space-y-1">
          <Label class="text-sm font-medium">DOI</Label>
          <p class="text-sm border rounded-md px-3 py-2 bg-muted/30">{{ paperData.doi || '—' }}</p>
        </div>
      </div>

      <!-- Key contributions — core of RESUME-05 -->
      <div class="space-y-2">
        <Label class="text-sm font-medium">Key Contributions</Label>
        <ul class="space-y-2">
          <li
            v-for="(contribution, i) in paperData.key_contributions"
            :key="i"
            class="flex gap-2 text-sm"
          >
            <span class="text-primary font-medium mt-0.5">•</span>
            <span>{{ contribution }}</span>
          </li>
        </ul>
      </div>

      <div class="space-y-1">
        <Label class="text-sm font-medium">Abstract</Label>
        <p class="text-sm text-muted-foreground leading-relaxed">{{ paperData.abstract || '—' }}</p>
      </div>
    </CardContent>
  </Card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { useResumeStore } from '@/stores/resume'

const resumeStore = useResumeStore()
const paperData = computed(() => resumeStore.paperData)
</script>
