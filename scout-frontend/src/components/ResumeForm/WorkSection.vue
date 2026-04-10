<template>
  <Card>
    <CardHeader><CardTitle>Work Experience</CardTitle></CardHeader>
    <CardContent class="space-y-6">
      <!-- D-07: useFieldArray display only — no push/remove exposed to user -->
      <div v-for="(entry, idx) in fields" :key="entry.key" class="border rounded-lg p-4 space-y-3">
        <div class="grid grid-cols-2 gap-3">
          <FormField :name="`work_experience[${idx}].company`" v-slot="{ field }">
            <FormItem>
              <FormLabel>Company</FormLabel>
              <FormControl>
                <Input :model-value="field.value as string" @update:model-value="field.onChange" />
              </FormControl>
            </FormItem>
          </FormField>
          <FormField :name="`work_experience[${idx}].title`" v-slot="{ field }">
            <FormItem>
              <FormLabel>Job Title</FormLabel>
              <FormControl>
                <Input :model-value="field.value as string" @update:model-value="field.onChange" />
              </FormControl>
            </FormItem>
          </FormField>
          <FormField :name="`work_experience[${idx}].start_date`" v-slot="{ field }">
            <FormItem>
              <FormLabel>Start Date</FormLabel>
              <FormControl>
                <Input :model-value="field.value as string" @update:model-value="field.onChange" placeholder="YYYY-MM" />
              </FormControl>
            </FormItem>
          </FormField>
          <FormField :name="`work_experience[${idx}].end_date`" v-slot="{ field }">
            <FormItem>
              <FormLabel>End Date</FormLabel>
              <FormControl>
                <Input :model-value="field.value as string" @update:model-value="field.onChange" placeholder="YYYY-MM or Present" />
              </FormControl>
            </FormItem>
          </FormField>
          <FormField :name="`work_experience[${idx}].location`" v-slot="{ field }">
            <FormItem>
              <FormLabel>Location</FormLabel>
              <FormControl>
                <Input :model-value="field.value as string" @update:model-value="field.onChange" />
              </FormControl>
            </FormItem>
          </FormField>
        </div>
        <!-- Bullets as textarea — newline-separated for readability -->
        <FormField :name="`work_experience[${idx}].bullets`" v-slot="{ field }">
          <FormItem>
            <FormLabel>Bullet Points <span class="text-muted-foreground text-xs">(one per line)</span></FormLabel>
            <FormControl>
              <Textarea
                :model-value="Array.isArray(field.value) ? (field.value as string[]).join('\n') : ''"
                @update:model-value="(v: string) => field.onChange(v.split('\n').filter((l: string) => l.trim()))"
                :rows="4"
                placeholder="Achieved X by doing Y, resulting in Z"
              />
            </FormControl>
          </FormItem>
        </FormField>
      </div>
      <p v-if="fields.length === 0" class="text-sm text-muted-foreground text-center py-4">
        No work experience was parsed from your resume.
      </p>
    </CardContent>
  </Card>
</template>

<script setup lang="ts">
import { useFieldArray } from 'vee-validate'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { FormField, FormItem, FormLabel, FormControl } from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
// D-07: only 'fields' exposed — no push, remove, swap operations available to user
const { fields } = useFieldArray('work_experience')
</script>
