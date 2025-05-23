from abc import ABC, abstractmethod
from datetime import datetime

from ActivityLevel import ActivityLevel

class Statuses(ABC):
    @abstractmethod
    def get_status_name(self):
        pass
    
    @abstractmethod
    def matches(self, repo_data, recent_commits, maintainer_activity):
        pass

class LiveStatus(Statuses):
    def get_status_name(self):
        return "Live"
    
    def matches(self, repo_data, recent_commits, maintainer_activity):
        if repo_data.get('archived', False):
            return False

        last_updated = datetime.fromisoformat(repo_data['updated_at'].replace('Z', '+00:00'))
        
        has_recent_activity = last_updated > ActivityLevel.Active.value
        has_recent_commits = recent_commits > 0
        has_maintainer_response = maintainer_activity is not None and ActivityLevel.Active
        
        return not repo_data.get('archived', False) and (has_recent_activity or has_recent_commits or has_maintainer_response)
        

class StagnantStatus(Statuses):
    def get_status_name(self):
        return "Stagnant"
    
    def matches(self, repo_data, recent_commits, maintainer_activity):
        if repo_data.get('archived', False):
            return False
        
        last_updated = datetime.fromisoformat(repo_data['updated_at'].replace('Z', '+00:00'))
        
        no_recent_contributions = last_updated <= ActivityLevel.someActivity.value and recent_commits == 0
        some_issue_activity = maintainer_activity is not None and ActivityLevel.someActivity
        
        return no_recent_contributions and some_issue_activity

class DeadStatus(Statuses):
    def get_status_name(self):
        return "Dead"
    
    def matches(self, repo_data, recent_commits, maintainer_activity):
        if repo_data.get('archived', False):
            return True
        
        last_updated = datetime.fromisoformat(repo_data['updated_at'].replace('Z', '+00:00'))
        
        no_recent_contributions = last_updated <= ActivityLevel.Inactive.value
        no_maintainer_response = maintainer_activity is False or maintainer_activity is None or ActivityLevel.Inactive
        
        return no_recent_contributions and no_maintainer_response and recent_commits == 0
