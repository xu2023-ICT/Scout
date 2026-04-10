<template>
  <Card>
    <CardHeader><CardTitle>Education</CardTitle></CardHeader>
    <CardContent class="space-y-4">
      <div v-for="(entry, idx) in fields" :key="entry.key" class="border rounded-lg p-4 space-y-3">
        <div class="grid grid-cols-2 gap-3">
          <FormField :name="`education[${idx}].institution`" v-slot="{ field }">
            <FormItem class="col-span-2">
              <FormLabel>Institution</FormLabel>
              <FormControl>
                <Input :model-value="field.value as string" @update:model-value="field.onChange" />
              </FormControl>
            </FormItem>
          </FormField>
          <FormField :name="`education[${idx}].degree`" v-slot="{ field }">
            <FormItem>
              <FormLabel>Degree</FormLabel>
              <FormControl>
                <Input :model-value="field.value as string" @update:model-value="field.onChange" placeholder="BS, MS, PhD..." />
              </FormControl>
            </FormItem>
          </FormField>
          <FormField :name="`education[${idx}].field`" v-slot="{ field }">
            <FormItem>
              <FormLabel>Field of Study</FormLabel>
              <FormControl>
                <Input :model-value="field.value as string" @update:model-value="field.onChange" />
              </FormControl>
            </FormItem>
          </FormField>
          <FormField :name="`education[${idx}].start_date`" v-slot="{ field }">
            <FormItem>
              <FormLabel>Start Date</FormLabel>
              <FormControl>
                <Input :model-value="field.value as string" @update:model-value="field.onChange" placeholder="YYYY" />
              </FormControl>
            </FormItem>
          </FormField>
          <FormField :name="`education[${idx}].end_date`" v-slot="{ field }">
            <FormItem>
              <FormLabel>End Date</FormLabel>
              <FormControl>
                <Input :model-value="field.value as string" @update:model-value="field.onChange" placeholder="YYYY or Present" />
              </FormControl>
            </FormItem>
          </FormField>
          <FormField :name="`education[${idx}].gpa`" v-slot="{ field }">
            <FormItem>
              <FormLabel>GPA</FormLabel>
              <FormControl>
                <Input :model-value="field.value as string" @update:model-value="field.onChange" placeholder="3.9/4.0" />
              </FormControl>
            </FormItem>
          </FormField>
        </div>
        <FormField :name="`education[${idx}].description`" v-slot="{ field }">
          <FormItem>
            <FormLabel>Notes</FormLabel>
            <FormControl>
              <Textarea :model-value="field.value as string" @update:model-value="field.onChange" :rows="2" />
            </FormControl>
          </FormItem>
        </FormField>
      </div>
      <p v-if="fields.length === 0" class="text-sm text-muted-foreground text-center py-4">No education entries parsed.</p>
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
const { fields } = useFieldArray('education')
</script>
