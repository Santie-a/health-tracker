import { MealDetail } from "@/features/nutrition/components/meal-detail";

export default async function MealPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <MealDetail id={Number(id)} />;
}
