import { FeedbackStatus } from '@/types/enums';
import { Tag } from 'antd';

export const FeedbackStatusLabels: Record<FeedbackStatus, string> = {
  [FeedbackStatus.PENDING]: 'Pending',
  [FeedbackStatus.ACCEPTED]: 'In Progress',
  [FeedbackStatus.RESOLVED]: 'Resolved',
};

export const FeedbackStatusTag: React.FC<{ status: FeedbackStatus }> = ({
  status,
}) => {
  switch (status) {
    case FeedbackStatus.PENDING:
      return <Tag color="default">{FeedbackStatusLabels[status]}</Tag>;
    case FeedbackStatus.ACCEPTED:
      return <Tag color="cyan">{FeedbackStatusLabels[status]}</Tag>;
    case FeedbackStatus.RESOLVED:
      return <Tag color="green">{FeedbackStatusLabels[status]}</Tag>;
    default:
      return null;
  }
};
