import streamlit as st
import time
from services.config.workout_config import METRICS_FIELDS
from services.persistence.exercise_repository import add_exercise


def save_workout_progress(exercise=None, metrics=None):
    exercise = exercise or st.session_state.get("exercise_type")

    if not exercise:
        return False

    total_reps = int(st.session_state.get("reps") or 0)
    reps_per_set = int(st.session_state.get("reps_per_set") or 0)
    last_saved_reps = int(st.session_state.get("last_saved_reps") or 0)
    last_saved_sets = int(st.session_state.get("last_saved_sets_completed") or 0)
    saved_reps = max(last_saved_reps, last_saved_sets * reps_per_set)
    unsaved_reps = max(total_reps - saved_reps, 0)

    if unsaved_reps <= 0:
        return False

    unsaved_sets = unsaved_reps // reps_per_set if reps_per_set > 0 else 0
    now_ts = time.time()
    started_at = st.session_state.get("set_cycle_started_at", now_ts)
    time_taken = max(now_ts - started_at, 0)
    user_id = st.session_state.get("user_id", 0)

    add_exercise(user_id, exercise, unsaved_reps, unsaved_sets, time_taken)

    if reps_per_set > 0:
        st.session_state.last_saved_sets_completed = total_reps // reps_per_set

    st.session_state.last_saved_reps = max(total_reps, saved_reps + unsaved_reps)
    st.session_state.set_cycle_started_at = now_ts
    return True


def sync_metrics_update(context):
    if not context or not hasattr(context, "state") or not context.state.playing:
        return
    
    processor = (
        getattr(context, "video_processor", None)
        or getattr(context, "video_transformer", None)
        or getattr(context, "_video_processor", None)
    )

    if not processor:
        return 
    
    exercise = st.session_state.get("exercise_type")

    if not exercise:
        return
    
    processor.set_exercise(exercise)
    latest_metrics = processor.get_latest_metrics()

    if not latest_metrics:
        st.session_state.tracking_status = "Waiting for camera frames..."
        return
    
    reps = latest_metrics.get("reps", 0)

    if reps is None:
        reps = 0
        
    st.session_state.reps = reps

    fields = METRICS_FIELDS.get(exercise)

    if not fields:
        return 

    for key, default in fields.items():
        st.session_state[key] = latest_metrics.get(key, default)

    reps_per_set = st.session_state.get("reps_per_set", 0)
    target_sets = st.session_state.get("target_sets", 0)

    if reps is not None and reps_per_set > 0 and target_sets > 0:
        sets_completed = reps // reps_per_set
        current_set_reps = reps % reps_per_set
        workout_completed = sets_completed >= target_sets 
    else:
        sets_completed = 0
        current_set_reps = 0
        workout_completed = False

    st.session_state.sets_completed = sets_completed
    st.session_state.current_set_reps = current_set_reps
    st.session_state.workout_completed = workout_completed

    last_saved_sets = st.session_state.get("last_saved_sets_completed", 0)

    if target_sets > 0 and reps_per_set > 0 and sets_completed > last_saved_sets:
        newly_completed = sets_completed - last_saved_sets
        now_ts = time.time()
        started_at = st.session_state.get("set_cycle_started_at", now_ts)
        time_taken = now_ts - started_at
        user_id = st.session_state.get("user_id", 0)

        add_exercise(user_id, exercise, newly_completed * reps_per_set, newly_completed, time_taken)

        if st.session_state.get("voice_pipeline"):
            result = st.session_state.voice_pipeline.process_event(
                event="set_completed",
                exercise=exercise,
                metrics=latest_metrics,
            )

            if result:
                st.session_state.audio_to_play, st.session_state.coach_feedback = result

        st.session_state.set_cycle_started_at = now_ts
        st.session_state.last_saved_sets_completed = sets_completed
        st.session_state.last_saved_reps = sets_completed * reps_per_set

    if workout_completed and not st.session_state.get("last_notified_workout_complete", False):
        st.session_state.last_notified_workout_complete = True

        if st.session_state.get("voice_pipeline"):
            result = st.session_state.voice_pipeline.process_event(
                event="workout_completed",
                exercise=exercise,
                metrics=latest_metrics,
            )

            if result:
                st.session_state.audio_to_play, st.session_state.coach_feedback = result
                
    pose_detected = latest_metrics.get("pose_detected", True)
    st.session_state.tracking_status = (
        "Tracking exercise movement"
        if pose_detected
        else latest_metrics.get("issue") or "Move into frame so the coach can see the exercise."
    )
    
    if not pose_detected and st.session_state.get("voice_pipeline"):
        result = st.session_state.voice_pipeline.process_event(
            event="no_pose_detected",
            exercise=exercise,
            metrics={"issue": "No pose detected! Please step into the camera frame."},
        )
    
        if result:
            st.session_state.audio_to_play, st.session_state.coach_feedback = result

    if st.session_state.get("voice_pipeline"):
        result = st.session_state.voice_pipeline.process_event(
            event="ongoing_form_check",
            exercise=exercise,
            metrics=latest_metrics,
        )
        
        if result:
            st.session_state.audio_to_play, st.session_state.coach_feedback = result
