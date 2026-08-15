# TP.3. Automated Focus Direction Prompt

## Purpose
To generate instructions for an AI video editor or visualizer to automatically direct the viewer's attention to the most relevant elements within a complex technical interface (e.g., workflow diagram, code editor, dashboard) through dynamic camera movements (zooms, pans).

## Prompt Structure
```
As a ZYNTH Master Strategist AI, your task is to provide "Automated Focus Direction" instructions for a video segment showcasing a [TECHNICAL INTERFACE TYPE, e.g., n8n workflow, code editor, analytics dashboard] related to [TOPIC/PROCESS].

Your instructions should guide an AI video editor to:
1.  Identify the key active or most relevant elements within the interface at specific timestamps or narrative points.
2.  Generate dynamic camera movements (zooms, pans, highlights) to draw the viewer's eye to these elements.
3.  Ensure the focus shifts smoothly and logically, following the narrative flow of the voiceover or on-screen text.

Consider the following context:
- Video Segment Duration: [DURATION, e.g., 15 seconds]
- Narrative Point 1: [DESCRIPTION OF WHAT IS BEING EXPLAINED, e.g., "the trigger node for the automation"]
- Corresponding Visual Element 1: [SPECIFIC UI ELEMENT TO FOCUS ON, e.g., "the 'Webhook' node at top left"]
- Narrative Point 2: [DESCRIPTION OF WHAT IS BEING EXPLAINED, e.g., "the Gemini model processing the request"]
- Corresponding Visual Element 2: [SPECIFIC UI ELEMENT TO FOCUS ON, e.g., "the 'Gemini Model' node in the center"]
- Overall Goal of Segment: [WHAT THE VIEWER SHOULD UNDERSTAND]

Generate a sequence of 3-5 focus direction commands, including the element to focus on and the type of camera movement.
```

## AI Integration Notes
- This prompt is crucial for making technical content engaging and understandable.
- The AI should be able to parse the technical interface (if provided as an image or description) to identify logical points of interest.
- The output should be directly actionable by an AI video editing tool capable of dynamic camera control.
