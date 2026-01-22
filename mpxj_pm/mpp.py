"""Leitura do .mpp via MPXJ (usado internamente pela importação)."""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


def _init_mpxj():
    try:
        import glob
        import os

        import mpxj

        if not mpxj.isJVMStarted():
            lib_dir = mpxj.mpxj_dir
            jar_files = glob.glob(os.path.join(lib_dir, "*.jar"))
            for jar in jar_files:
                try:
                    mpxj.addClassPath(jar)
                except Exception:
                    pass
            mpxj.startJVM()

        from jpype.types import JClass

        try:
            return JClass("org.mpxj.reader.UniversalProjectReader")
        except TypeError:
            return JClass("net.sf.mpxj.reader.UniversalProjectReader")

    except ImportError:
        print("Erro: O pacote 'mpxj' não está instalado.")
        print("Instale com: pip install -r requirements.txt")
        raise


UniversalProjectReader = _init_mpxj()


class MPPReader:
    """Classe para ler e processar arquivos Microsoft Project"""

    def __init__(self, mpp_file_path: str):
        self.mpp_file_path = Path(mpp_file_path)
        if not self.mpp_file_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {mpp_file_path}")
        self.project = None

    def read(self):
        reader = UniversalProjectReader()
        self.project = reader.read(str(self.mpp_file_path))
        return self.project

    def get_project_info(self) -> Dict[str, Any]:
        if not self.project:
            self.read()

        props = self.project.getProjectProperties()
        
        project_id = None
        try:
            if hasattr(self.project, "getID"):
                project_id = self.project.getID()
            elif hasattr(self.project, "getUniqueID"):
                project_id = self.project.getUniqueID()
            
            if project_id is None:
                if hasattr(props, "getUniqueID"):
                    project_id = props.getUniqueID()
                elif hasattr(props, "getID"):
                    project_id = props.getID()
                elif hasattr(props, "getProjectID"):
                    project_id = props.getProjectID()
        except Exception:
            pass
        
        return {
            "id": str(project_id) if project_id is not None else None,
            "name": str(props.getProjectTitle()) if props.getProjectTitle() else None,
            "start_date": self._convert_date(props.getStartDate()),
            "finish_date": self._convert_date(props.getFinishDate()),
            "author": str(props.getAuthor()) if props.getAuthor() else None,
            "company": str(props.getCompany()) if props.getCompany() else None,
            "comments": str(props.getComments()) if props.getComments() else None,
            "creation_date": self._convert_date(props.getCreationDate()),
            "last_saved": self._convert_date(
                props.getLastSaved()
                if hasattr(props, "getLastSaved")
                else (props.getLastSavedDate() if hasattr(props, "getLastSavedDate") else None)
            ),
        }

    def get_tasks(self) -> List[Dict[str, Any]]:
        if not self.project:
            self.read()

        tasks: List[Dict[str, Any]] = []
        for task in self.project.getTasks():
            if task is None:
                continue

            tasks.append(
                {
                    "id": str(task.getID()) if task.getID() else None,
                    "name": str(task.getName()) if task.getName() else None,
                    "start": self._convert_date(task.getStart()),
                    "finish": self._convert_date(task.getFinish()),
                    "duration": self._convert_duration(task.getDuration()),
                    "work": self._convert_duration(task.getWork()),
                    "percent_complete": int(task.getPercentageComplete()) if task.getPercentageComplete() else 0,
                    "priority": self._convert_priority(task.getPriority()),
                    "notes": str(task.getNotes()) if task.getNotes() else None,
                    "wbs": str(task.getWBS()) if task.getWBS() else None,
                    "outline_level": int(task.getOutlineLevel()) if task.getOutlineLevel() else 0,
                    "milestone": bool(task.getMilestone()) if task.getMilestone() else False,
                    "summary": bool(task.getSummary()) if task.getSummary() else False,
                }
            )

        return tasks

    def get_resources(self) -> List[Dict[str, Any]]:
        if not self.project:
            self.read()

        resources: List[Dict[str, Any]] = []
        for resource in self.project.getResources():
            if resource is None:
                continue

            resources.append(
                {
                    "id": str(resource.getID()) if resource.getID() else None,
                    "name": str(resource.getName()) if resource.getName() else None,
                    "email": str(resource.getEmailAddress()) if resource.getEmailAddress() else None,
                    "type": str(resource.getType()) if resource.getType() else None,
                    "group": str(resource.getGroup()) if resource.getGroup() else None,
                    "max_units": float(resource.getMaxUnits()) if resource.getMaxUnits() else None,
                    "standard_rate": self._convert_rate(resource.getStandardRate()),
                    "cost": self._convert_rate(resource.getCost()),
                    "notes": str(resource.getNotes()) if resource.getNotes() else None,
                }
            )

        return resources

    def get_assignments(self) -> List[Dict[str, Any]]:
        if not self.project:
            self.read()

        assignments: List[Dict[str, Any]] = []
        for assignment in self.project.getResourceAssignments():
            if assignment is None:
                continue

            task = assignment.getTask()
            resource = assignment.getResource()

            assignments.append(
                {
                    "task_id": str(task.getID()) if task and task.getID() else None,
                    "task_name": str(task.getName()) if task and task.getName() else None,
                    "resource_id": str(resource.getID()) if resource and resource.getID() else None,
                    "resource_name": str(resource.getName()) if resource and resource.getName() else None,
                    "work": self._convert_duration(assignment.getWork()),
                    "cost": self._convert_rate(assignment.getCost()),
                    "start": self._convert_date(assignment.getStart()),
                    "finish": self._convert_date(assignment.getFinish()),
                    "units": float(assignment.getUnits()) if assignment.getUnits() else None,
                    "percent_complete": int(assignment.getPercentageWorkComplete())
                    if hasattr(assignment, "getPercentageWorkComplete") and assignment.getPercentageWorkComplete()
                    else (
                        int(assignment.getPercentageComplete())
                        if hasattr(assignment, "getPercentageComplete") and assignment.getPercentageComplete()
                        else 0
                    ),
                }
            )

        return assignments

    def get_dependencies(self) -> List[Dict[str, Any]]:
        if not self.project:
            self.read()

        dependencies: List[Dict[str, Any]] = []
        for task in self.project.getTasks():
            if task is None:
                continue

            predecessors = task.getPredecessors()
            if not predecessors:
                continue

            for predecessor in predecessors:
                target_task = None
                if hasattr(predecessor, "getTargetTask"):
                    target_task = predecessor.getTargetTask()
                elif hasattr(predecessor, "getPredecessorTask"):
                    target_task = predecessor.getPredecessorTask()
                elif hasattr(predecessor, "getSourceTask"):
                    target_task = predecessor.getSourceTask()

                dependencies.append(
                    {
                        "predecessor_id": str(target_task.getID()) if target_task and target_task.getID() else None,
                        "predecessor_name": str(target_task.getName()) if target_task and target_task.getName() else None,
                        "successor_id": str(task.getID()) if task.getID() else None,
                        "successor_name": str(task.getName()) if task.getName() else None,
                        "type": str(predecessor.getType()) if hasattr(predecessor, "getType") and predecessor.getType() else None,
                        "lag": self._convert_duration(predecessor.getLag() if hasattr(predecessor, "getLag") else None),
                    }
                )

        return dependencies

    def get_calendars(self) -> List[Dict[str, Any]]:
        if not self.project:
            self.read()

        calendars: List[Dict[str, Any]] = []
        for calendar in self.project.getCalendars():
            if calendar is None:
                continue

            parent = calendar.getParent() if hasattr(calendar, "getParent") else None
            calendar_id = None
            if hasattr(calendar, "getID"):
                calendar_id = calendar.getID()
            elif hasattr(calendar, "getUniqueID"):
                calendar_id = calendar.getUniqueID()

            parent_id = None
            if parent is not None:
                if hasattr(parent, "getID"):
                    parent_id = parent.getID()
                elif hasattr(parent, "getUniqueID"):
                    parent_id = parent.getUniqueID()

            calendars.append(
                {
                    "id": str(calendar_id) if calendar_id else None,
                    "name": str(calendar.getName()) if hasattr(calendar, "getName") and calendar.getName() else None,
                    "parent": str(parent.getName())
                    if parent and hasattr(parent, "getName") and parent.getName()
                    else None,
                    "parent_id": str(parent_id) if parent_id else None,
                }
            )

        return calendars

    def _convert_date(self, date_obj) -> Optional[str]:
        if date_obj is None:
            return None
        try:
            if hasattr(date_obj, "getTime"):
                timestamp = date_obj.getTime() / 1000.0
                return datetime.fromtimestamp(timestamp).isoformat()
            if isinstance(date_obj, datetime):
                return date_obj.isoformat()
            return str(date_obj)
        except Exception:
            return None

    def _convert_duration(self, duration_obj) -> Optional[float]:
        if duration_obj is None:
            return None
        try:
            if hasattr(duration_obj, "getDuration"):
                return float(duration_obj.getDuration())
            return float(duration_obj)
        except Exception:
            return None

    def _convert_rate(self, rate_obj) -> Optional[float]:
        if rate_obj is None:
            return None
        try:
            if hasattr(rate_obj, "getAmount"):
                return float(rate_obj.getAmount())
            return float(rate_obj)
        except Exception:
            return None

    def _convert_priority(self, priority_obj) -> Optional[int]:
        if priority_obj is None:
            return None
        try:
            if hasattr(priority_obj, "getValue"):
                return int(priority_obj.getValue())
            if hasattr(priority_obj, "intValue"):
                return int(priority_obj.intValue())
            return int(priority_obj)
        except Exception:
            return None


def read_mpp(mpp_path: str) -> Dict[str, Any]:
    """Convenience: retorna todos os blocos necessários para importação."""
    r = MPPReader(mpp_path)
    r.read()
    return {
        "project": r.get_project_info(),
        "tasks": r.get_tasks(),
        "resources": r.get_resources(),
        "assignments": r.get_assignments(),
        "dependencies": r.get_dependencies(),
        "calendars": r.get_calendars(),
    }
