<template>
  <Card>
    <CardHeader><CardTitle>Personal Information</CardTitle></CardHeader>
    <CardContent class="grid grid-cols-2 gap-4">
      <FormField name="personal.name" v-slot="{ field, errorMessage }">
        <FormItem class="col-span-2">
          <FormLabel>Full Name *</FormLabel>
          <FormControl>
            <Input
              :model-value="field.value as string"
              @update:model-value="field.onChange"
              placeholder="Your name"
            />
          </FormControl>
          <FormMessage>{{ errorMessage }}</FormMessage>
        </FormItem>
      </FormField>
      <FormField name="personal.email" v-slot="{ field }">
        <FormItem>
          <FormLabel>Email</FormLabel>
          <FormControl>
            <Input
              :model-value="field.value as string"
              @update:model-value="field.onChange"
              type="email"
            />
          </FormControl>
        </FormItem>
      </FormField>
      <FormField name="personal.phone" v-slot="{ field }">
        <FormItem>
          <FormLabel>Phone</FormLabel>
          <FormControl>
            <Input
              :model-value="field.value as string"
              @update:model-value="field.onChange"
            />
          </FormControl>
        </FormItem>
      </FormField>
      <FormField name="personal.location" v-slot="{ field }">
        <FormItem>
          <FormLabel>Location</FormLabel>
          <FormControl>
            <Input
              :model-value="field.value as string"
              @update:model-value="field.onChange"
              placeholder="City, Country"
            />
          </FormControl>
        </FormItem>
      </FormField>
      <FormField name="personal.linkedin" v-slot="{ field }">
        <FormItem>
          <FormLabel>LinkedIn</FormLabel>
          <FormControl>
            <Input
              :model-value="field.value as string"
              @update:model-value="field.onChange"
              type="url"
            />
          </FormControl>
        </FormItem>
      </FormField>
      <FormField name="personal.github" v-slot="{ field }">
        <FormItem class="col-span-2">
          <FormLabel>GitHub URL <span class="text-muted-foreground text-xs">(read-only — set at upload)</span></FormLabel>
          <FormControl>
            <Input
              :model-value="field.value as string"
              @update:model-value="field.onChange"
              type="url"
              disabled
              class="opacity-60"
            />
          </FormControl>
        </FormItem>
      </FormField>
      <FormField name="personal.summary" v-slot="{ field }">
        <FormItem class="col-span-2">
          <FormLabel>Summary</FormLabel>
          <FormControl>
            <Textarea
              :model-value="field.value as string"
              @update:model-value="field.onChange"
              :rows="3"
              placeholder="Brief professional summary"
            />
          </FormControl>
        </FormItem>
      </FormField>
    </CardContent>
  </Card>
</template>

<script setup lang="ts">
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { FormField, FormItem, FormLabel, FormControl, FormMessage } from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
</script>
