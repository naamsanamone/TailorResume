import { useContext } from 'react';

import {
  SortableRegion,
  SortableTemplateSection,
  useSectionLayoutRuntime,
} from '@/helpers/section-layout';
import { StateContext } from '@/modules/builder/resume/ResumeLayout';
import { pageStyle } from '@/templates/common/palette-ui';
import { useResumePalette } from '@/templates/common/resumePalette';

import { Education } from './components/Education';
import { Header } from './components/Header';
import { Skills } from './components/Skills';
import { Summary } from './components/Summary';
import { Work } from './components/Work';

export default function CleanTemplate() {
  const data = useContext(StateContext);
  const { regions } = useSectionLayoutRuntime();
  const p = useResumePalette();
  const basics = data.basics;

  const renderSection = (sectionId: string) => {
    switch (sectionId) {
      case 'summary':
        return <Summary summary={basics.summary} p={p} />;
      case 'work':
        return <Work work={data.work} p={p} />;
      case 'education':
        return <Education education={data.education} p={p} />;
      case 'skills':
        return <Skills skills={data.skills} p={p} />;
      default:
        return null;
    }
  };

  return (
    <div style={{ ...pageStyle(p), padding: '48px 56px' }}>
      <Header basics={basics} p={p} />
      <SortableRegion regionId="main" items={regions.main}>
        {(id) => (
          <SortableTemplateSection key={id} id={id}>
            {renderSection(id)}
          </SortableTemplateSection>
        )}
      </SortableRegion>
    </div>
  );
}
