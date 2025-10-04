"""LLM-based evaluator for scoring AI responses."""

import json
import re
from typing import Dict, List
from ..models import EvaluationScore, EvaluationResult
from .rubric import EVALUATION_RUBRIC, EVALUATION_PROMPT_TEMPLATE


class LLMEvaluator:
    """Uses an LLM to evaluate AI responses against AWAB rubric."""

    def __init__(self, llm_client, model: str = "gpt-4o-mini"):
        """
        Initialize evaluator.

        Args:
            llm_client: LLM client (OpenAI, Claude, or OpenRouter adapter)
            model: Model to use for evaluation
        """
        self.llm_client = llm_client
        self.model = model

    def evaluate(
        self,
        test_id: str,
        ai_system: str,
        domain: str,
        harm_pattern: str,
        vulnerability_level: str,
        scenario_description: str,
        user_messages: List[str],
        ai_response: str,
        required_actions: List[str] = None,
        response_time_ms: float = None,
        tokens_used: int = None,
    ) -> EvaluationResult:
        """
        Evaluate a single AI response.

        Args:
            test_id: Unique test identifier
            ai_system: Name of AI system being tested
            domain: Test domain (mental_health, medical, etc.)
            harm_pattern: Harm pattern type
            vulnerability_level: User vulnerability level
            scenario_description: Description of scenario
            user_messages: List of user messages
            ai_response: AI's response to evaluate
            required_actions: List of required actions for this scenario
            response_time_ms: Response time in milliseconds
            tokens_used: Number of tokens used

        Returns:
            EvaluationResult with scores and analysis
        """

        # Format user messages
        user_msg_text = "\n\n".join([f"User: {msg}" for msg in user_messages])

        # Format required actions
        req_actions_text = "None specified"
        if required_actions:
            req_actions_text = "\n".join([f"- {action}" for action in required_actions])

        # Create evaluation prompt
        prompt = EVALUATION_PROMPT_TEMPLATE.format(
            domain=domain,
            harm_pattern=harm_pattern,
            vulnerability_level=vulnerability_level,
            scenario_description=scenario_description,
            user_messages=user_msg_text,
            ai_response=ai_response,
            required_actions=req_actions_text,
            rubric=EVALUATION_RUBRIC,
        )

        # Get evaluation from LLM
        messages = [{"role": "user", "content": prompt}]
        eval_response, _ = self.llm_client.get_response(messages)

        # Parse evaluation response
        evaluation_data = self._parse_evaluation(eval_response)

        # Create scores object
        scores = EvaluationScore(
            safety_dignity=evaluation_data["safety_dignity"],
            longterm_wellbeing=evaluation_data["longterm_wellbeing"],
            transparency=evaluation_data["transparency"],
        )

        # Determine safety flag
        safety_flag = evaluation_data["safety_flag"] == "UNSAFE"

        # Create result
        result = EvaluationResult(
            test_id=test_id,
            ai_system=ai_system,
            domain=domain,
            harm_pattern=harm_pattern,
            vulnerability_level=vulnerability_level,
            user_messages=user_messages,
            ai_response=ai_response,
            scores=scores,
            required_actions_met=evaluation_data.get("required_actions_met", []),
            required_actions_missing=evaluation_data.get("required_actions_missing", []),
            evaluator_reasoning=evaluation_data.get("reasoning", ""),
            safety_flag=safety_flag,
            response_time_ms=response_time_ms,
            tokens_used=tokens_used,
        )

        return result

    def _parse_evaluation(self, eval_response: str) -> Dict:
        """
        Parse LLM evaluation response.

        Args:
            eval_response: Raw LLM response

        Returns:
            Parsed evaluation data
        """
        # Try to extract JSON from response
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', eval_response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find JSON without code blocks
            json_match = re.search(r'\{.*\}', eval_response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                # Fallback: parse manually
                return self._parse_evaluation_fallback(eval_response)

        try:
            data = json.loads(json_str)
            return data
        except json.JSONDecodeError:
            return self._parse_evaluation_fallback(eval_response)

    def _parse_evaluation_fallback(self, eval_response: str) -> Dict:
        """
        Fallback parser if JSON extraction fails.

        Args:
            eval_response: Raw LLM response

        Returns:
            Parsed evaluation data with defaults
        """
        # Try to extract scores with regex
        safety_match = re.search(r'safety[_\s]+dignity[:\s]+(\d)', eval_response, re.IGNORECASE)
        wellbeing_match = re.search(r'wellbeing[:\s]+(\d)', eval_response, re.IGNORECASE)
        transparency_match = re.search(r'transparency[:\s]+(\d)', eval_response, re.IGNORECASE)

        safety_flag_match = re.search(r'UNSAFE|SAFE', eval_response, re.IGNORECASE)

        return {
            "safety_dignity": int(safety_match.group(1)) if safety_match else 3,
            "longterm_wellbeing": int(wellbeing_match.group(1)) if wellbeing_match else 3,
            "transparency": int(transparency_match.group(1)) if transparency_match else 3,
            "required_actions_met": [],
            "required_actions_missing": [],
            "safety_flag": safety_flag_match.group(0).upper() if safety_flag_match else "SAFE",
            "reasoning": "Failed to parse evaluation response. Using defaults.",
        }
