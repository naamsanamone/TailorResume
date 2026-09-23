import { TemplateSlider } from './TemplatesSlider';

export const TemplateSelect = () => {
  return (
    <div
      className={`md:h-[380px] md:w-[720px] bg-white flex flex-col px-3 md:px-10 py-[23px] shadow-2xl`}
    >
      <TemplateSlider />
    </div>
  );
};
