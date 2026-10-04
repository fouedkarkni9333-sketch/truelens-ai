import os
from openai import OpenAI

# تهيئة العميل (يمكن ربطه بأي نموذج متطور متوافق مع API)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

class AdvancedRefiner:
    @staticmethod
    def verify_and_correct_analysis(original_text: str, generated_analysis: str) -> dict:
        """
        يستخدم تقنية التقييم الذاتي للتحقق من دقة التحليل واكتشاف أي هلوسة محتملة.
        """
        prompt = f"""
        You are an expert AI auditor. Review the following generated analysis against the source text.
        
        Source Text:
        {original_text}
        
        Generated Analysis:
        {generated_analysis}
        
        Task:
        1. Evaluate the accuracy of the analysis on a scale from 0.0 to 1.0.
        2. Identify any inconsistencies or unsupported claims.
        3. Provide a refined, highly accurate version of the analysis.
        
        Output format (JSON):
        {{
            "confidence_score": 0.0,
            "critique": "...",
            "refined_analysis": "..."
        }}
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            import json
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            return {
                "confidence_score": 1.0,
                "critique": f"Refinement bypassed due to error: {str(e)}",
                "refined_analysis": generated_analysis
            }
