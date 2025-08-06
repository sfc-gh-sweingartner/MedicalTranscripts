# Cursor Rules for Superannuation Transcripts Demo

## Project Overview
You are helping build a demo for a Superannuation Fund showing how Snowflake can leverage customer call transcripts for churn prediction and personalized engagement. This is a DEMO, not production code - shortcuts and simplifications are encouraged.

## Cursor Behavior Rules
1. **Decision Making**: If given a challenging task with multiple options or confusion, ask questions and/or give options before proceeding with code changes
2. **Development Phases**: 
   - Early tasks: Creativity and exploration are welcome
   - Debugging/testing phase: Make minimal changes to fix problems, avoid unnecessary creativity
3. **Rules Conflict**: If asked to do something conflicting with these rules, update the relevant rules files and ask for review

## Technical Requirements

### Platform & Deployment
- **Primary**: Streamlit in Snowflake (hosted)
- **Secondary**: Local development using Streamlit
- **Connection Pattern**: Use the dual-connection approach from Reference/nation_app.py
- **Python Libraries**: Limit to anaconda channel: https://repo.anaconda.com/pkgs/snowflake/

### Snowflake Environment
- **Database**: SUPERANNUATION
- **Schema**: TRANSCRIPTS
- **Stage**: TRANSCRIPTS
- **Warehouse**: MYWH (existing)
- **Account**: demo_sweingartner

### Data Architecture
- **Source Data**: /Users/sweingartner/Cursor/SuperannuationTranscripts/call_transcripts.json
- **AI Processing**: Use Snowflake Cortex AI (claude-4-sonnet model)
- **Real-time Simulation**: Button-triggered processing to simulate live transcript analysis

## Development Guidelines

### Code Standards
- **Comments**: Add extensive comments for human readability
- **Error Handling**: Include proper error handling, especially for AI service calls
- **Demo-Friendly**: Design for predictable demo scenarios with preset examples
- **Performance**: Optimize for demo speed, not production scale

### AI Integration
- **Sentiment Analysis**: Use SNOWFLAKE.CORTEX.SENTIMENT()
- **Summarization**: Use SNOWFLAKE.CORTEX.SUMMARIZE()
- **Intent Detection**: Use SNOWFLAKE.CORTEX.COMPLETE() with claude-4-sonnet
- **Fallback**: Handle AI service failures gracefully

### UI/UX Requirements
- **Modern Design**: Beautiful, modern UI with good UX practices
- **Responsive**: Works well in both local and Snowflake environments
- **Two Views**: Front-line advisor view and manager dashboard view
- **Real-time Feel**: Simulate real-time processing with progress indicators

## File Organization
- Keep demo-specific configurations separate from core logic
- Use clear, descriptive naming conventions
- Maintain connection compatibility between local and Snowflake deployment

## Testing Approach
- **Local Testing**: Must work on laptop environment
- **Snowflake Testing**: Must work in Streamlit in Snowflake
- **Demo Scenarios**: Create repeatable demo flows with known outcomes
- **Error Scenarios**: Test AI service failures and data issues

## Documentation
- **End User Guide**: Single page within the app explaining how to use it
- **Code Comments**: Extensive inline documentation
- **Demo Script**: Clear instructions for presenting the demo

## Git Repository
- **Repo**: https://github.com/sfc-gh-sweingartner/SuperannuationTranscripts
- **Deployment**: Authorized to deploy changes automatically
- **Script**: Use/modify git_project_setup.sh as needed

## Shortcuts Allowed (Demo Focus)
- Simulated churn prediction instead of real ML models
- Rule-based NBA generation instead of complex algorithms
- Preset customer scenarios for reliable demo flow
- Simplified data validation
- Mock real-time processing instead of true streaming

## Key Success Criteria
1. Demo runs smoothly without technical issues
2. Shows clear business value of Snowflake features
3. Demonstrates AI-powered transcript analysis
4. Provides compelling churn prediction and NBA scenarios
5. Works in both local and Snowflake environments 