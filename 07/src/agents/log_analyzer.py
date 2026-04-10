"""
Log Analyzer Agent - orchestrates model, tools, memory, and prompts
"""
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

from ..models.gemini import GeminiModel
from ..tools import get_log_tools
from ..utils.response import extract_response_text
from ..config import Config


class LogAnalyzerAgent:
    """
    AI Logging Agent

    Capabilities:
    - Read and analyze log files
    - Answer questions about logs
    - Maintain conversation history

    Limitations:
    - No routing decisions
    - No automated actions
    - No multi-source integration
    """

    def __init__(self):
        """Initialize the agent"""
        # Initialize model
        self.model = GeminiModel()
        self.llm = self.model.get_llm()

        # Get tools
        self.tools = get_log_tools()

        # Bind tools to model
        self.llm_with_tools = self.model.get_llm_with_tools(self.tools)

        # Create chat memory
        self.chat_history = InMemoryChatMessageHistory()

        # Create prompt
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", Config.get_system_prompt()),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
        ])

        # Create chain
        chain = self.prompt | self.llm_with_tools

        # Wrap with message history
        self.chain_with_history = RunnableWithMessageHistory(
            chain,
            lambda session_id: self.chat_history,
            input_messages_key="input",
            history_messages_key="chat_history",
        )

        self.session_id = "default_session"

    def process_query(self, user_input: str) -> str:
        """
        Process a user query and return the response.

        Args:
            user_input: User's question or command

        Returns:
            String containing the agent's response
        """
        try:
            # Get response from chain with history
            response = self.chain_with_history.invoke(
                {"input": user_input},
                config={"configurable": {"session_id": self.session_id}}
            )

            # Check if model wants to use tools
            if hasattr(response, 'tool_calls') and response.tool_calls:
                return self._handle_tool_calls(response, user_input)
            else:
                # Direct response without tools
                response_text = extract_response_text(response)

                # Add to chat history
                self.chat_history.add_user_message(user_input)
                self.chat_history.add_ai_message(response_text)

                return response_text

        except Exception as e:
            error_msg = f"Error processing query: {str(e)}"
            print(f"\n{error_msg}")
            import traceback
            traceback.print_exc()
            return error_msg

    def _handle_tool_calls(self, response, user_input: str) -> str:
        """Handle tool calls from the model"""
        tool_results = []

        # Execute each tool call
        for tool_call in response.tool_calls:
            tool_name = tool_call['name']
            tool_args = tool_call['args']

            # Find the tool
            tool_func = None
            for tool in self.tools:
                if tool.name == tool_name:
                    tool_func = tool
                    break

            if tool_func:
                try:
                    result = tool_func.invoke(tool_args)
                    tool_results.append({
                        'tool': tool_name,
                        'result': result
                    })
                except Exception as e:
                    tool_results.append({
                        'tool': tool_name,
                        'result': f"Error: {str(e)}"
                    })

        # Ask model to analyze results
        analysis_prompt = f"User asked: {user_input}\n\n"
        analysis_prompt += "Tool results:\n"
        for tr in tool_results:
            analysis_prompt += f"\n{tr['tool']}:\n{tr['result']}\n"
        analysis_prompt += "\nPlease analyze these results and answer the user's question."

        final_response = self.llm.invoke(analysis_prompt)
        response_text = extract_response_text(final_response)

        # Update chat history
        self.chat_history.add_user_message(user_input)
        self.chat_history.add_ai_message(response_text)

        return response_text
